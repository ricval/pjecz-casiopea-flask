# 📝 Historial de Cambios (Changelog)

Todos los cambios notables en este proyecto serán documentados en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [1.2.0] - 2026-05-19

### ✨ Mejoras

- Creación de un nuevo módulo llamado `exp_juzgados`. El cual contiene los juzgados de los cuales se pueden pedir expedientes. Utilizado en el servicio "Revisión de Expedientes" de la unidad "Archivo".
- Añadida la columna `instrucciones` a la tabla de `cit_servicios`. Para incluir instrucciones de cómo llenar el campo de `notas` cuando se crea una cita nueva.
- Añadido formulario de "Asistencia" en módulo de citas. Para validar la asistencia de un cliente a su cita.
- Mejora del archivo `README.md`, se incluyó instrucciones de migración.
- Añadido archivo `CHANGELOG.md` para ver el historial de cambios. Es este archivo.
- Barra de progreso para el CLI de eliminar citas pasadas. Para no esperar sin ver cambios en la consola cuando se ejecuta el comando.
- Dejando todo preparado para migración de historial de citas programas _legacy_.

## [1.1.3] - 2026-05-07

### ✨ Mejoras

- Cambio de manejador de paquetes de `poetry` a `uv`. El manejador `uv` es más rápido y fácil de utilizar.