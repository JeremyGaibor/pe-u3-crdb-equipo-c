USE tiendatech;

ALTER TABLE pedidos
PARTITION BY LIST (provincia_entrega) (
    PARTITION pedidos_los_rios
        VALUES IN ('LOS RIOS'),

    PARTITION pedidos_guayas
        VALUES IN ('GUAYAS'),

    PARTITION pedidos_pichincha
        VALUES IN ('PICHINCHA'),

    PARTITION pedidos_manabi
        VALUES IN ('MANABI'),

    PARTITION pedidos_azuay
        VALUES IN ('AZUAY')
);
