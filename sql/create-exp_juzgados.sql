-- Creación de la tabla `exp_juzgados` para su nuevo módulo
-- Además añade el nuevo módulo a la tabla de módulos y permisos.
-- Fecha: 2026-05-19

-- Creación de la tabla `exp_juzgados` que utiliza el módulo Juzgados
CREATE TABLE exp_juzgados (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave VARCHAR(16) NOT NULL UNIQUE,
    descripcion_corta VARCHAR(64) NOT NULL,
    descripcion VARCHAR(256) NOT NULL,
    creado TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    modificado TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    estatus CHAR(1) NOT NULL DEFAULT 'A'
);

-- Hacemos que la tabla de `modulos` el campo `id` tipo `uuid` sea autogenerado
ALTER TABLE modulos 
ALTER COLUMN id SET DEFAULT gen_random_uuid();

-- Añadir módulo nuevo 'EXP_JUZGADOS' a la tabla de 'modulos'
INSERT INTO modulos (nombre, nombre_corto, icono, ruta, en_navegacion)
VALUES ('EXP JUZGADOS', 'Juzgados en expedientes', 'mdi mdi-gavel', '/exp_juzgados', TRUE);

-- Hacemos que la tabla de `permisos` el campo `id` tipo `uuid` sea autogenerado
ALTER TABLE permisos 
ALTER COLUMN id SET DEFAULT gen_random_uuid();

-- Añadir a la tabla de `permisos` que el rol ADMINISTRADOR pueda administrar el nuevo módulo 'EXP JUZGADOS'
INSERT INTO permisos (rol_id, modulo_id, nombre, nivel)
SELECT 
    r.id AS rol_id, 
    m.id AS modulo_id, 
    'ADMINISTRADOR puede ADMINISTRAR en EXP JUZGADOS' AS nombre, 
    4 AS nivel
FROM roles r, modulos m
WHERE r.nombre = 'ADMINISTRADOR' 
  AND m.nombre = 'EXP JUZGADOS';