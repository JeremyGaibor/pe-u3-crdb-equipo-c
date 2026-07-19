# PE-U3 — Clúster CockroachDB — Equipo C

Implementación y verificación de un clúster de base de datos distribuida de tres nodos con CockroachDB, aplicado al PFC **AGLS — TiendaTech**.

La práctica demuestra:

- configuración de un clúster CockroachDB de tres nodos;
- creación del esquema relacional de TiendaTech;
- carga reproducible de al menos 10 000 pedidos;
- fragmentación horizontal por provincia;
- tolerancia a fallos mediante la caída de un nodo;
- comparación de rendimiento entre el clúster y una instancia de nodo único.

---

## Integrantes

| Integrante | Rama | Responsabilidad |
|---|---|---|
| Jeremy Ruperto Gaibor Rodríguez | `Gaibor` | Configuración Docker, clúster y nodo único |
| Freddy Vladimir Farinango Guandinango | `Farinango` | Esquema, carga de datos y fragmentación |
| Iván Andrés Villamarín Cuenca | `Villamarin` | Consultas, benchmark y evidencias |

---

## PFC de referencia

**Código:** AGLS  
**Nombre:** TiendaTech  
**Descripción:** plataforma de comercio electrónico de hardware con asistente de compatibilidad.

TiendaTech fue seleccionado porque sus pedidos pueden organizarse mediante fragmentación horizontal por provincia de entrega. Esta distribución permite representar un escenario en el que los datos se almacenan y replican dentro de un clúster de tres nodos, conservando disponibilidad ante la caída de uno de ellos.

---

## Tecnologías utilizadas

- Docker Desktop 4.x
- Docker Compose Plugin
- CockroachDB `v24.3.0`
- Python 3.10 o superior
- `psycopg2-binary`
- `Faker`
- Git y GitHub
- LaTeX con `biblatex`, `booktabs`, `listings` y `tikz`

---

## Estructura del repositorio

```text
pe-u3-crdb-equipo-c/
├── README.md
├── docker-compose.yml
├── docker-compose-single.yml
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
    ├── resultados.csv
    ├── video_tolerancia.mp4
    └── demás capturas del experimento
