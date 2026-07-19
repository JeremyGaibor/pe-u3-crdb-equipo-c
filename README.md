# PE-U3 — Clúster CockroachDB — Equipo C

Implementación y verificación de un clúster de base de datos distribuida de tres nodos con CockroachDB, aplicado al PFC **AGLS — TiendaTech**.

La práctica permite demostrar:

- configuración de un clúster CockroachDB de tres nodos;
- implementación del esquema relacional de TiendaTech;
- carga reproducible de 10 000 pedidos;
- fragmentación horizontal por provincia;
- tolerancia a fallos ante la caída de un nodo;
- recuperación y reintegración automática;
- comparación de rendimiento entre el clúster y un nodo único.

---

## Repositorio público

URL del repositorio:

```text
URL_DEL_REPOSITORIO
```

> Antes de entregar, verificar que la URL pueda abrirse y clonarse sin iniciar sesión.

---

## Integrantes

| Integrante | Rama | Responsabilidad |
|---|---|---|
| Jeremy Ruperto Gaibor Rodríguez | `Gaibor` | Configuración del clúster, nodo único y documentación |
| Freddy Vladimir Farinango Guandinango | `Farinango` | Esquema, carga de datos y fragmentación |
| Iván Andrés Villamarín Cuenca | `Villamarin` | Tolerancia a fallos, consultas, benchmark y evidencias |

---

## PFC de referencia

**Código:** AGLS  
**Título:** TiendaTech — Plataforma de comercio electrónico de hardware con asistente de compatibilidad.

TiendaTech fue seleccionado porque la información de los pedidos puede organizarse mediante fragmentación horizontal según la provincia de entrega. Este criterio permite representar la distribución lógica de los datos y comprobar su disponibilidad dentro de un clúster de tres nodos. Además, el dominio facilita la ejecución de consultas de ventas, clientes y pedidos, así como la evaluación de replicación, tolerancia a fallos y rendimiento frente a una instancia de nodo único.

---

## Tecnologías utilizadas

- Docker Desktop 4.x
- Docker Compose Plugin
- CockroachDB `v24.3.0`
- Python 3.10 o superior
- `psycopg2-binary`
- `Faker`
- Git y GitHub
- LaTeX con `biblatex`, `booktabs`, `listings`, `tikz` y `pgfplots`

### Verificación de versiones

```powershell
docker --version
docker compose version
python --version
python -m pip show psycopg2-binary faker
```

Las versiones exactas de las dependencias deben quedar registradas en `requirements.txt`.

Para generarlo:

```powershell
python -m pip freeze |
Select-String "psycopg2-binary|Faker" |
Set-Content requirements.txt
```

Para instalar las versiones registradas:

```powershell
python -m pip install -r requirements.txt
```

---

## Estructura del repositorio

```text
pe-u3-crdb-equipo-c/
├── README.md
├── docker-compose.yml
├── docker-compose-single.yml
├── requirements.txt
├── LICENSE
├── .gitignore
├── sql/
│   ├── 01_schema.sql
│   ├── 02_partitions.sql
│   └── 03_queries.sql
├── scripts/
│   ├── seed_data.py
│   └── run_benchmark.py
├── docs/
│   ├── PE_U3_Informe.tex
│   ├── PE_U3_Informe.pdf
│   └── references.bib
└── evidencia/
    ├── dashboard.png
    ├── node_status.png
    ├── carga_10000_registros.png
    ├── particiones_pedidos.png
    ├── show_ranges_antes_fallo.png
    ├── show_ranges_durante_fallo.png
    ├── nodo2_reintegrado.png
    ├── benchmark_cluster.png
    ├── benchmark_nodo_unico.png
    ├── resultados_comparacion.png
    ├── resultados.csv
    └── video_tolerancia.mp4
```

---

# Ejecución rápida

Los siguientes comandos permiten reproducir la implementación principal desde la raíz del repositorio.

## 1. Instalar dependencias

```powershell
python -m pip install -r requirements.txt
```

## 2. Levantar el clúster

```powershell
docker compose up -d
```

## 3. Inicializar el clúster

Solo debe ejecutarse la primera vez:

```powershell
docker exec -it crdb-node1 cockroach init `
  --insecure `
  --host=crdb-node1:26357
```

## 4. Crear el esquema

```powershell
Get-Content -Raw .\sql\01_schema.sql |
docker exec -i crdb-node1 cockroach sql `
  --insecure `
  --host=crdb-node1:26257
```

## 5. Cargar los datos

```powershell
python .\scripts\seed_data.py --puerto 26257
```

## 6. Aplicar las particiones

```powershell
Get-Content -Raw .\sql\02_partitions.sql |
docker exec -i crdb-node1 cockroach sql `
  --insecure `
  --host=crdb-node1:26257
```

## 7. Ejecutar el benchmark del clúster

```powershell
python .\scripts\run_benchmark.py `
  --modo cluster `
  --puerto 26257
```

---

# Procedimiento completo

## 1. Levantamiento del clúster

Validar la configuración:

```powershell
docker compose config
```

Levantar los tres nodos:

```powershell
docker compose up -d
```

Comprobar los contenedores:

```powershell
docker compose ps
```

Deben aparecer:

```text
crdb-node1
crdb-node2
crdb-node3
```

Esperar hasta que los servicios finalicen su proceso de inicio.

---

## 2. Inicialización y verificación

Inicializar el clúster una sola vez:

```powershell
docker exec -it crdb-node1 cockroach init `
  --insecure `
  --host=crdb-node1:26357
```

Si aparece:

```text
cluster has already been initialized
```

significa que los volúmenes contienen un clúster previamente inicializado y no es necesario repetir el comando.

Verificar los nodos:

```powershell
docker exec -it crdb-node1 cockroach node status `
  --insecure `
  --host=crdb-node1:26257
```

Los tres nodos deben presentar:

```text
is_live = true
```

Dashboard:

```text
http://localhost:8080
```

---

## 3. Creación del esquema de TiendaTech

Ejecutar:

```powershell
Get-Content -Raw .\sql\01_schema.sql |
docker exec -i crdb-node1 cockroach sql `
  --insecure `
  --host=crdb-node1:26257
```

Verificar las tablas:

```powershell
docker exec -it crdb-node1 cockroach sql `
  --insecure `
  --host=crdb-node1:26257 `
  --database=tiendatech `
  -e "SHOW TABLES;"
```

Tablas esperadas:

```text
clientes
productos
pedidos
detalle_pedido
```

El esquema contiene claves primarias, claves foráneas, restricciones `CHECK` y restricciones `UNIQUE`.

---

## 4. Carga reproducible de datos

Ejecutar:

```powershell
python .\scripts\seed_data.py --puerto 26257
```

El script utiliza semillas fijas para producir datos reproducibles:

```text
Clientes: 1000
Productos: 500
Pedidos: 10000
Detalles: cantidad generada por el script
```

Verificar las cantidades:

```powershell
docker exec -it crdb-node1 cockroach sql `
  --insecure `
  --host=crdb-node1:26257 `
  --database=tiendatech `
  -e "SELECT COUNT(*) AS total_pedidos FROM pedidos;"
```

Resultado esperado:

```text
10000
```

---

## 5. Fragmentación horizontal

La tabla principal `pedidos` utiliza:

```sql
PARTITION BY LIST (provincia_entrega)
```

Las particiones corresponden a:

- Los Ríos
- Guayas
- Pichincha
- Manabí
- Azuay

Aplicar la fragmentación:

```powershell
Get-Content -Raw .\sql\02_partitions.sql |
docker exec -i crdb-node1 cockroach sql `
  --insecure `
  --host=crdb-node1:26257
```

Verificar las particiones:

```powershell
docker exec -it crdb-node1 cockroach sql `
  --insecure `
  --host=crdb-node1:26257 `
  --database=tiendatech `
  -e "SHOW PARTITIONS FROM TABLE pedidos;"
```

Verificar los rangos:

```powershell
docker exec -it crdb-node1 cockroach sql `
  --insecure `
  --host=crdb-node1:26257 `
  --database=tiendatech `
  -e "SHOW RANGES FROM TABLE pedidos;"
```

---

## 6. Prueba de tolerancia a fallos

### Estado inicial

```powershell
docker compose ps
```

```powershell
docker exec -it crdb-node1 cockroach node status `
  --insecure `
  --host=crdb-node1:26257
```

### Consulta inicial

```powershell
docker exec -it crdb-node1 cockroach sql `
  --insecure `
  --host=crdb-node1:26257 `
  --database=tiendatech `
  -e "SELECT COUNT(*) AS total_pedidos FROM pedidos;"
```

Resultado:

```text
10000
```

### Detener el nodo 2

```powershell
docker stop crdb-node2
```

Verificar:

```powershell
docker compose ps -a
```

El nodo 2 debe aparecer detenido, mientras los nodos 1 y 3 permanecen activos.

### Consulta durante el fallo

```powershell
docker exec -it crdb-node1 cockroach sql `
  --insecure `
  --host=crdb-node1:26257 `
  --database=tiendatech `
  -e "SELECT COUNT(*) AS total_pedidos FROM pedidos;"
```

El resultado debe continuar siendo:

```text
10000
```

### Verificación de rangos

Esperar 30 segundos:

```powershell
Start-Sleep -Seconds 30
```

Ejecutar:

```powershell
docker exec -it crdb-node1 cockroach sql `
  --insecure `
  --host=crdb-node1:26257 `
  --database=tiendatech `
  -e "SHOW RANGES FROM TABLE pedidos;"
```

### Reintegración

Reiniciar el nodo:

```powershell
docker start crdb-node2
```

Verificar hasta que vuelva a aparecer activo:

```powershell
docker exec -it crdb-node1 cockroach node status `
  --insecure `
  --host=crdb-node1:26257
```

Tiempo de reintegración medido:

```text
X segundos
```

Reemplazar `X` por el tiempo obtenido durante la prueba real.

El video continuo de la prueba se encuentra en:

```text
evidencia/video_tolerancia.mp4
```

Duración permitida:

```text
Mínimo: 2 minutos
Máximo: 5 minutos
```

---

## 7. Consultas de rendimiento

El archivo `sql/03_queries.sql` contiene:

1. JOIN entre pedidos y clientes.
2. GROUP BY por provincia.
3. Consulta puntual por clave primaria.
4. Consulta de rango.
5. Subconsulta correlacionada.

Todas utilizan:

```sql
EXPLAIN ANALYZE
```

Ejecutar:

```powershell
Get-Content -Raw .\sql\03_queries.sql |
docker exec -i crdb-node1 cockroach sql `
  --insecure `
  --host=crdb-node1:26257 `
  --database=tiendatech
```

---

## 8. Benchmark del clúster

```powershell
python .\scripts\run_benchmark.py `
  --modo cluster `
  --puerto 26257
```

Cada consulta se ejecuta cinco veces y se calcula su tiempo promedio.

Los resultados se almacenan en:

```text
evidencia/resultados.csv
```

---

## 9. Instancia de nodo único

Validar:

```powershell
docker compose -f docker-compose-single.yml config
```

Levantar:

```powershell
docker compose -f docker-compose-single.yml up -d
```

Verificar:

```powershell
docker compose -f docker-compose-single.yml ps
```

Configuración:

```text
Puerto SQL externo: 26260
Dashboard: http://localhost:8083
```

El archivo `docker-compose-single.yml` debe contener:

```yaml
container_name: crdb-single
```

---

## 10. Preparación del nodo único

Crear el esquema:

```powershell
Get-Content -Raw .\sql\01_schema.sql |
docker exec -i crdb-single cockroach sql `
  --insecure `
  --host=crdb-single:26257
```

Aplicar las particiones:

```powershell
Get-Content -Raw .\sql\02_partitions.sql |
docker exec -i crdb-single cockroach sql `
  --insecure `
  --host=crdb-single:26257
```

Cargar los mismos datos:

```powershell
python .\scripts\seed_data.py --puerto 26260
```

Verificar:

```powershell
docker exec -it crdb-single cockroach sql `
  --insecure `
  --host=crdb-single:26257 `
  --database=tiendatech `
  -e "SELECT COUNT(*) AS total_pedidos FROM pedidos;"
```

Resultado esperado:

```text
10000
```

---

## 11. Benchmark del nodo único

```powershell
python .\scripts\run_benchmark.py `
  --modo single `
  --puerto 26260
```

El archivo `evidencia/resultados.csv` se actualiza con:

- tiempo del clúster;
- tiempo del nodo único;
- factor de mejora;
- interpretación cualitativa.

Consultar:

```powershell
Get-Content .\evidencia\resultados.csv
```

---

## Resultados generales

En el entorno local utilizado, el nodo único presentó menores tiempos promedio en las cinco consultas.

Esto se explica porque el conjunto de datos es reducido y el clúster requiere operaciones adicionales de coordinación, comunicación y replicación. El principal beneficio del clúster no fue disminuir la latencia local, sino proporcionar:

- replicación;
- disponibilidad;
- tolerancia a fallos;
- recuperación automática;
- escalabilidad horizontal.

---

## Detener los entornos

Detener el clúster sin eliminar los volúmenes:

```powershell
docker compose down
```

Detener el nodo único:

```powershell
docker compose -f docker-compose-single.yml down
```

No utilizar:

```powershell
docker compose down -v
```

salvo que se desee eliminar permanentemente los datos almacenados.

---

## Evidencias

Las evidencias del experimento se encuentran en:

```text
evidencia/
```

Incluyen:

- dashboard con los tres nodos;
- salida de `node status`;
- carga de 10 000 pedidos;
- particiones;
- rangos antes y durante el fallo;
- reintegración del nodo 2;
- benchmark del clúster;
- benchmark del nodo único;
- archivo `resultados.csv`;
- video de tolerancia a fallos.

---

## Informe técnico

El informe académico se encuentra en:

```text
docs/PE_U3_Informe.tex
docs/PE_U3_Informe.pdf
docs/references.bib
```

---

## Licencia

El proyecto se distribuye bajo la licencia MIT.

Consultar:

```text
LICENSE
```

---

## Declaración de uso de IA generativa

Se utilizó ChatGPT como herramienta de apoyo para revisar comandos, detectar errores de configuración, organizar la documentación y mejorar la redacción técnica. El equipo verificó manualmente el funcionamiento de los scripts, comandos, consultas, configuraciones y evidencias incluidas en el repositorio.
