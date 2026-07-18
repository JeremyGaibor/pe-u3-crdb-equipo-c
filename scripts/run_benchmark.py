import argparse
import csv
import re
import statistics
from pathlib import Path

import psycopg2

CONSULTAS = {
    "Q1_JOIN": """
        SELECT
            p.pedido_id,
            c.nombre,
            p.provincia_entrega,
            p.estado,
            p.total
        FROM pedidos AS p
        JOIN clientes AS c
            ON p.cliente_id = c.cliente_id
        LIMIT 100;
    """,

    "Q2_GROUP_BY": """
        SELECT
            provincia_entrega,
            COUNT(*) AS cantidad_pedidos,
            SUM(total) AS ventas_totales,
            AVG(total) AS promedio_venta
        FROM pedidos
        GROUP BY provincia_entrega
        ORDER BY ventas_totales DESC;
    """,

    "Q3_CLAVE_PRIMARIA": """
        SELECT
            pedido_id,
            cliente_id,
            fecha_pedido,
            provincia_entrega,
            estado,
            total
        FROM pedidos
        WHERE provincia_entrega = 'MANABI'
          AND pedido_id = 1;
    """,

    "Q4_RANGO": """
        SELECT
            pedido_id,
            fecha_pedido,
            provincia_entrega,
            estado,
            total
        FROM pedidos
        WHERE fecha_pedido BETWEEN
              current_timestamp() - INTERVAL '180 days'
              AND current_timestamp()
          AND total BETWEEN 500 AND 3000
        ORDER BY fecha_pedido DESC;
    """,

    "Q5_SUBCONSULTA": """
        SELECT
            c.cliente_id,
            c.nombre,
            c.provincia
        FROM clientes AS c
        WHERE (
            SELECT COUNT(*)
            FROM pedidos AS p
            WHERE p.cliente_id = c.cliente_id
        ) > 5
        LIMIT 100;
    """,
}

ARCHIVO_RESULTADOS = (
    Path(__file__).resolve().parent.parent
    / "evidencia"
    / "resultados.csv"
)

REPETICIONES = 5

def obtener_argumentos():
    parser = argparse.ArgumentParser(
        description="Benchmark de consultas CockroachDB"
    )

    parser.add_argument(
        "--modo",
        choices=["cluster", "single"],
        required=True,
        help="Entorno que se desea medir",
    )

    parser.add_argument(
        "--puerto",
        type=int,
        required=True,
        help="Puerto SQL de CockroachDB",
    )

    return parser.parse_args()

def extraer_tiempo(plan):
    patron = r"execution time:\s*([\d.]+)(ms|µs)"

    coincidencia = re.search(
        patron,
        plan,
        re.IGNORECASE,
    )

    if coincidencia is None:
        raise ValueError(
            "No se encontró execution time en EXPLAIN ANALYZE"
        )

    valor = float(coincidencia.group(1))
    unidad = coincidencia.group(2)

    if unidad == "µs":
        valor = valor / 1000

    return valor

def medir_consulta(cursor, consulta):
    tiempos = []

    for _ in range(REPETICIONES):
        cursor.execute(
            "EXPLAIN ANALYZE " + consulta
        )

        filas = cursor.fetchall()

        plan = "\n".join(
            str(fila[0])
            for fila in filas
        )

        tiempos.append(
            extraer_tiempo(plan)
        )

    return round(
        statistics.mean(tiempos),
        3,
    )

def leer_resultados():
    if not ARCHIVO_RESULTADOS.exists():
        return {}

    resultados = {}

    with ARCHIVO_RESULTADOS.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as archivo:
        lector = csv.DictReader(archivo)

        for fila in lector:
            resultados[fila["consulta"]] = fila

    return resultados

def interpretar(cluster, single):
    if cluster is None or single is None:
        return "Pendiente de comparación"

    if cluster < single:
        return "El clúster presentó menor tiempo promedio"

    if cluster > single:
        return "El nodo único presentó menor tiempo promedio"

    return "Los tiempos fueron equivalentes"

def guardar_resultados(modo, mediciones):
    resultados = leer_resultados()

    for nombre, tiempo in mediciones.items():
        fila = resultados.get(
            nombre,
            {
                "consulta": nombre,
                "tiempo_cluster_ms": "",
                "tiempo_nodo_unico_ms": "",
                "factor_mejora": "",
                "interpretacion": "",
            },
        )

        if modo == "cluster":
            fila["tiempo_cluster_ms"] = str(tiempo)
        else:
            fila["tiempo_nodo_unico_ms"] = str(tiempo)

        cluster_texto = fila["tiempo_cluster_ms"]
        single_texto = fila["tiempo_nodo_unico_ms"]

        cluster = (
            float(cluster_texto)
            if cluster_texto
            else None
        )

        single = (
            float(single_texto)
            if single_texto
            else None
        )

        if cluster is not None and single is not None:
            factor = (
                single / cluster
                if cluster > 0
                else 0
            )

            fila["factor_mejora"] = str(
                round(factor, 3)
            )

        fila["interpretacion"] = interpretar(
            cluster,
            single,
        )

        resultados[nombre] = fila

    ARCHIVO_RESULTADOS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    columnas = [
        "consulta",
        "tiempo_cluster_ms",
        "tiempo_nodo_unico_ms",
        "factor_mejora",
        "interpretacion",
    ]

    with ARCHIVO_RESULTADOS.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=columnas,
        )

        escritor.writeheader()

        for nombre in CONSULTAS:
            escritor.writerow(resultados[nombre])

def ejecutar():
    argumentos = obtener_argumentos()

    conexion = psycopg2.connect(
        host="localhost",
        port=argumentos.puerto,
        database="tiendatech",
        user="root",
        sslmode="disable",
    )

    mediciones = {}

    try:
        with conexion.cursor() as cursor:
            for nombre, consulta in CONSULTAS.items():
                print(f"Ejecutando {nombre}...")

                tiempo = medir_consulta(
                    cursor,
                    consulta,
                )

                mediciones[nombre] = tiempo

                print(
                    f"Promedio: {tiempo} ms"
                )

    finally:
        conexion.close()

    guardar_resultados(
        argumentos.modo,
        mediciones,
    )

    print(
        "\nResultados guardados en:"
    )
    print(ARCHIVO_RESULTADOS)

if __name__ == "__main__":
    ejecutar()
