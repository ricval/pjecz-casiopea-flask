-- 2026-06-12
-- Añadir módulo de Agendas

-- Insertar el módulo de Agendas
INSERT INTO modulos (id, nombre, nombre_corto, icono, ruta, en_navegacion)
VALUES (
    gen_random_uuid(),
    'AGENDAS',
    'Agendas',
    'mdi mdi-calendar-month',
    '/agendas',
    true
);

-- Insertar el permiso de Agendas para el rol de Administrador con nivel 4 (ADMINISTRAR)
INSERT INTO permisos (id, rol_id, modulo_id, nombre, nivel)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM roles WHERE nombre = 'ADMINISTRADOR'),
    (SELECT id FROM modulos WHERE nombre = 'AGENDAS'),
    'ADMINISTRADOR puede ADMINISTRAR en AGENDAS',
    4
);
