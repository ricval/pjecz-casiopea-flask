-- Actualización para la versión v1.5.0

-- Añadir módulo nuevo 'CIT CITAS TURNOS' a la tabla de 'modulos'
INSERT INTO modulos (nombre, nombre_corto, icono, ruta, en_navegacion)
VALUES ('CIT CITAS TURNOS', 'Citas-Turnos', 'mdi mdi-room-service', '/cit_citas_turnos', TRUE);

-- Añadir a la tabla de `permisos` que el rol ADMINISTRADOR pueda administrar el nuevo módulo 'CIT CITAS TURNOS'
INSERT INTO permisos (rol_id, modulo_id, nombre, nivel)
SELECT 
    r.id AS rol_id, 
    m.id AS modulo_id, 
    'ADMINISTRADOR puede ADMINISTRAR en CIT CITAS TURNOS' AS nombre, 
    4 AS nivel
FROM roles r, modulos m
WHERE r.nombre = 'ADMINISTRADOR' 
  AND m.nombre = 'CIT CITAS TURNOS';
