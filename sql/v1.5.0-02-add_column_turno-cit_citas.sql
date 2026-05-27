-- Añadir columna turno en la tabla `cit_citas`
ALTER TABLE cit_citas ADD COLUMN turno_id INT;
ALTER TABLE cit_citas ADD COLUMN turno VARCHAR(16);
COMMENT ON COLUMN cit_citas.turno IS 'Almacena el turno generado para el cliente al registrar su asistencia (ej. A-001).';

-- Añadir columna turnos_unidad_id en la tabla `oficinas`
ALTER TABLE oficinas ADD COLUMN turnos_unidad_id INT;
