USE tiendatech;

-- Consulta 1: JOIN entre pedidos y clientes
EXPLAIN ANALYZE
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

-- Consulta 2: GROUP BY por provincia
EXPLAIN ANALYZE
SELECT
    provincia_entrega,
    COUNT(*) AS cantidad_pedidos,
    SUM(total) AS ventas_totales,
    AVG(total) AS promedio_venta
FROM pedidos
GROUP BY provincia_entrega
ORDER BY ventas_totales DESC;

-- Consulta 3: búsqueda puntual por clave
EXPLAIN ANALYZE
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

-- Consulta 4: consulta de rango
EXPLAIN ANALYZE
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

-- Consulta 5: subconsulta correlacionada
EXPLAIN ANALYZE
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