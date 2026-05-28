# 📝 Historial de Cambios (Changelog)

Todos los cambios notables en este proyecto serán documentados en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [1.5.0] - 2026-05-29

### ✨ Mejoras

- Añadir campo `unidad id - Turnos` en el formulario del módulo `oficina`. Para poder hacer un entendimiento entre el sistema de citas y el de turnos.
- Para _Test_ se añadió un archivo `*.json` en el directorio `test`. Pero se añadió en el archivo `.gitignore` que no suba los archivos de prueba, solo los ejemplos.
- Creada prueba de conexión con el sistema de turnos.
- Crear servicio de turnos. Conexión con la API del sistema de turnos. 
- Añadida página de pruebas.
- Añadido página de configuración para el lector de código de barras.
- Añadido nuevo módulo `cit_citas_turnos`. Que muestra una página para leer el código de barras y marcar la asistencia y crear un nuevo turno en el sistema de turnos.
- Añadido nuevo campo `turnos_unidad_id` en la tabla `oficinas`. Para establecer que unidad elegir al momento de crear un turno nuevo en el sistema de turnos.
- Añadido nuevos campos `turno_id` y `turno` en la tabla `cit_citas`. Para guardar el turno generado por el sistema de citas al escanear el código de barras de asistencia.
- Añadidos los campos de código de barras en el modelo de `cit_citas`. Es nuevo campo sirve para marcar la asistencia del cliente y añadir un nuevo turno al sistema de turnos.

### ⚙️ Requerimientos

- Actualización de BD, ejecutar _scripts_ con `psql -f [nombre_archivo.sql]`:
    - `v1.5.0-01-add_modulo.sql`
    - `v1.5.0-02-add_column_turno-cit-citas.sql`

- Variables de entorno:
    - `TURNOS_API_KEY`: Es la API-Key para comunicarse con el sistema de turnos.
    - `TURNOS_API_KEY_URL`: Es la URL que se utiliza para comunicarse con el sistema de turnos.

- Archivo de prueba:
    - `test_crear_turno.json`

## [1.4.0] - 2026-05-22

### ✨ Mejoras

- Creación de un nuevo módulo llamado `exp_juzgados`. El cual contiene los juzgados de los cuales se pueden pedir expedientes. Utilizado especialmente en el servicio "Revisión de Expedientes" de la unidad "Archivo".

### 🐞 Arreglado

- En el detalle de `categorías` no se mostraba el detalle en sí de la categoría.

## [1.3.0] - 2026-05-21

### ✨ Mejoras

- Añadido archivo CLI `cit-clientes-registros` con el comando `eliminar` para que se ejecute todos los días y limpie los usuarios que no pudieron completar su registro y puedan volver a intentarlo.
- Añadido archivo CLI `cit-clientes-recuperaciones` con el comando `eliminar` para que se ejecute todos los días y limpie las recuperaciones hechas por los clientes de su contraseña y permita hacer otra.
- Envío de reporte de citas programadas para el siguiente día hábil a cada usuario de cada oficina.
- Creación de plantilla de reporte para próximas citas agendadas.
- Integración del servicio de envío de email.
- Añadido número de versión y fecha de deploy en el menú izquierdo. Para saber exactamente que versión está desplegada.

### 🐞 Arreglado

- Botones en listado de citas, para las diferentes vistas del día, se quedaban activados al seleccionar el botón "inactivos".

***

## [1.2.0] - 2026-05-20

### ✨ Mejoras

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