# 📝 Historial de Cambios (Changelog)

Todos los cambios notables en este proyecto serán documentados en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [1.2.0] - 2026-05-20

### ✨ Mejoras

- Creación de un nuevo módulo llamado `exp_juzgados`. El cual contiene los juzgados de los cuales se pueden pedir expedientes. Utilizado en el servicio "Revisión de Expedientes" de la unidad "Archivo".
- Vista de "citas para hoy", "citas para mañana" y "todas". Solo se muestran las citas del día indicado. Para que sea más fácil localizar la cita que llega y anotar su "código de asistencia".
- Añadida la columna `instrucciones` a la tabla de `cit_servicios`. Para incluir instrucciones de cómo llenar el campo de `notas` cuando se crea una cita nueva.
- Añadido formulario de "Asistencia" en módulo de citas. Para validar la asistencia de un cliente a su cita.
- Mejora del archivo `README.md`, se incluyó instrucciones de migración.
- Añadido archivo `CHANGELOG.md` para ver el historial de cambios. Es este archivo.
- Barra de progreso para el CLI de eliminar citas pasadas. Para no esperar sin ver cambios en la consola cuando se ejecuta el comando.
- Dejando todo preparado para migración de historial de citas programas _legacy_.

### 🛠️ Cambios

- Quitar columna de "Creado" en el listado de citas. Confunde saber cuando fue creada con la fecha en que se agendó la cita.
- Código de acceso en detalle solo visible para Administradores.

### 🐞 Arreglado

- Formulario de edición de 'Oficinas'. Los campos select con uuid no se seleccionaban correctamente.
- Formulario de edición de 'Servicios'. Los campos select con uuid no se seleccionaban correctamente.
- En columna 'Fecha' del listado de citas. Al utilizar la función `moment()` no mostraba la fecha correctamente.
- Listado de citas por 'Autoridad'. Filtrando solo las citas pertenecientes a dicha oficina.

## [1.1.3] - 2026-05-07

### ✨ Mejoras

- Cambio de manejador de paquetes de `poetry` a `uv`. El manejador `uv` es más rápido y fácil de utilizar.