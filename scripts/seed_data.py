import random
import argparse
from datetime import datetime, timedelta
from decimal import Decimal

import psycopg2
from faker import Faker
from psycopg2.extras import execute_values

# Semillas para obtener siempre datos reproducibles
random.seed(42)
Faker.seed(42)

fake = Faker("es_ES")

def obtener_argumentos():
    parser = argparse.ArgumentParser(
        description="Carga de datos para TiendaTech"
    )

    parser.add_argument(
        "--puerto",
        type=int,
        default=26257,
        help="Puerto SQL de CockroachDB",
    )

    return parser.parse_args()

TOTAL_CLIENTES = 1_000
TOTAL_PRODUCTOS = 500
TOTAL_PEDIDOS = 10_000

PROVINCIAS = [
    "LOS RIOS",
    "GUAYAS",
    "PICHINCHA",
    "MANABI",
    "AZUAY",
]

CATEGORIAS = [
    "PROCESADORES",
    "TARJETAS GRAFICAS",
    "MEMORIAS RAM",
    "ALMACENAMIENTO",
    "PLACAS MADRE",
    "PERIFERICOS",
]

ESTADOS = [
    "PENDIENTE",
    "PAGADO",
    "ENVIADO",
    "ENTREGADO",
    "CANCELADO",
]

def crear_clientes():
    clientes = []

    for cliente_id in range(1, TOTAL_CLIENTES + 1):
        clientes.append(
            (
                cliente_id,
                fake.name(),
                f"cliente{cliente_id}@tiendatech.com",
                random.choice(PROVINCIAS),
                fake.date_time_between(
                    start_date="-2y",
                    end_date="now",
                ),
            )
        )

    return clientes

def crear_productos():
    productos = []

    for producto_id in range(1, TOTAL_PRODUCTOS + 1):
        categoria = random.choice(CATEGORIAS)
        precio = Decimal(
            str(round(random.uniform(10, 1500), 2))
        )
        stock = random.randint(0, 500)

        productos.append(
            (
                producto_id,
                f"{categoria.title()} {producto_id}",
                categoria,
                precio,
                stock,
            )
        )

    return productos

def crear_pedidos_y_detalles():
    pedidos = []
    detalles = []
    detalle_id = 1

    fecha_inicial = datetime.now() - timedelta(days=730)

    for pedido_id in range(1, TOTAL_PEDIDOS + 1):
        cliente_id = random.randint(1, TOTAL_CLIENTES)
        provincia = random.choice(PROVINCIAS)
        estado = random.choice(ESTADOS)
        fecha = fecha_inicial + timedelta(
            days=random.randint(0, 729),
            seconds=random.randint(0, 86399),
        )

        cantidad_detalles = random.randint(1, 3)
        total_pedido = Decimal("0.00")

        detalles_temporales = []

        for _ in range(cantidad_detalles):
            producto_id = random.randint(1, TOTAL_PRODUCTOS)
            cantidad = random.randint(1, 5)
            precio_unitario = Decimal(
                str(round(random.uniform(10, 1500), 2))
            )
            subtotal = precio_unitario * cantidad
            total_pedido += subtotal

            detalles_temporales.append(
                (
                    detalle_id,
                    pedido_id,
                    producto_id,
                    cantidad,
                    precio_unitario,
                    subtotal,
                )
            )

            detalle_id += 1

        pedidos.append(
            (
                pedido_id,
                cliente_id,
                fecha,
                provincia,
                estado,
                total_pedido,
            )
        )

        detalles.extend(detalles_temporales)

    return pedidos, detalles

def insertar_datos():
    conexion = None

    try:
        argumentos = obtener_argumentos()
        conexion = psycopg2.connect(
          host="localhost",
          port=argumentos.puerto,
          database="tiendatech",
          user="root",
          sslmode="disable",
        )
    
        conexion.autocommit = False

        with conexion.cursor() as cursor:
            print("Limpiando datos anteriores...")

            cursor.execute(
                """
                TRUNCATE TABLE
                    detalle_pedido,
                    pedidos,
                    productos,
                    clientes
                CASCADE;
                """
            )

            clientes = crear_clientes()
            productos = crear_productos()
            pedidos, detalles = crear_pedidos_y_detalles()

            print("Insertando clientes...")

            execute_values(
                cursor,
                """
                INSERT INTO clientes (
                    cliente_id,
                    nombre,
                    correo,
                    provincia,
                    fecha_registro
                )
                VALUES %s
                """,
                clientes,
                page_size=500,
            )

            print("Insertando productos...")

            execute_values(
                cursor,
                """
                INSERT INTO productos (
                    producto_id,
                    nombre,
                    categoria,
                    precio,
                    stock
                )
                VALUES %s
                """,
                productos,
                page_size=500,
            )

            print("Insertando 10 000 pedidos...")

            execute_values(
                cursor,
                """
                INSERT INTO pedidos (
                    pedido_id,
                    cliente_id,
                    fecha_pedido,
                    provincia_entrega,
                    estado,
                    total
                )
                VALUES %s
                """,
                pedidos,
                page_size=1_000,
            )

            print("Insertando detalles de pedidos...")

            execute_values(
                cursor,
                """
                INSERT INTO detalle_pedido (
                    detalle_id,
                    pedido_id,
                    producto_id,
                    cantidad,
                    precio_unitario,
                    subtotal
                )
                VALUES %s
                """,
                detalles,
                page_size=1_000,
            )

        conexion.commit()

        print("\nCarga terminada correctamente.")
        print(f"Clientes: {len(clientes)}")
        print(f"Productos: {len(productos)}")
        print(f"Pedidos: {len(pedidos)}")
        print(f"Detalles: {len(detalles)}")

    except Exception as error:
        if conexion is not None:
            conexion.rollback()

        print(f"\nError durante la carga: {error}")
        raise

    finally:
        if conexion is not None:
            conexion.close()

if __name__ == "__main__":
    insertar_datos()