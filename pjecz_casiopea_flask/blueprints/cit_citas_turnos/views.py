"""
Cit Citas Turnos, vistas
"""
from typing import Tuple

from flask import Blueprint, abort, render_template, request, url_for, render_template_string
from flask_login import current_user, login_required

from ...lib.safe_string import safe_email, safe_message, safe_string, safe_uuid
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..cit_clientes.models import CitCliente
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from ..cit_citas.models import CitCita

MODULO = "CIT CITAS TURNOS"

cit_citas_turnos = Blueprint(
    "cit_citas_turnos",
    __name__,
    template_folder="templates",
    static_folder="static",  # Añadimos la carpeta de archivos estáticos
)


@cit_citas_turnos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cit_citas_turnos.route("/cit_citas_turnos", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def captura():
    """Creación del turno en el sistema de turnos"""

    if "barcode" in request.form:
        codigo_barras = request.form["barcode"]
        cit_cita = CitCita.query.filter_by(codigo_barras=codigo_barras).first()
        if cit_cita is None:
            return render_template("cit_citas_turnos/captura.jinja2", error="¡Su código de barras ya no es válido!")
        # if cit_cita.oficina.turnos_unidad_id is None:
        #     return render_template("cit_citas_turnos/captura.jinja2", error="Error del sistema: Esta oficina no tiene unidad de turnos asignada")
        if cit_cita.turno is None:
            turno_id, turno = _crear_turno(cit_cita.oficina.turnos_unidad_id)
            cit_cita.turno_id = turno_id
            cit_cita.turno = turno
            # cit_cita.save()
        return render_template("cit_citas_turnos/captura.jinja2", cit_cita=cit_cita)

    return render_template("cit_citas_turnos/captura.jinja2")


def _crear_turno(unidad_id: int)-> Tuple[int, str]:
    """
    Crea un nuevo turno en el sistema de turnos
    :return El id del turno generado y el número de turno compuesto.
    """

    return (418, f"OCP-{1}")


@cit_citas_turnos.route("/cit_citas_turnos/config/<int:paso_id>", methods=["GET"])
@permission_required(MODULO, Permiso.CREAR)
def config(paso_id):
    """Proceso para la configuración del lector de código de barras"""

    # Pasos de configuración para el lector de código de barras
    pasos_config = [
        {
            "titulo": "Restaurar valores de fábrica",
            "texto": "Escanee este código para restaurar el lector a sus valores predeterminados de fábrica.",
            "qr_img": url_for(
                "cit_citas_turnos.static",
                filename="img/config/paso-01-reiniciar.png",
            ),
        },
        {
            "titulo": "Conectar por cable",
            "texto": "Lo configura para que se conecta al PC por cable.",
            "qr_img": url_for(
                "cit_citas_turnos.static",
                filename="img/config/paso-02-conectar-por-cable.png",
            ),
        },
        {
            "titulo": "Desactivar voz",
            "texto": "Desactiva las respuestas con voz.",
            "qr_img": url_for(
                "cit_citas_turnos.static",
                filename="img/config/paso-03-desactivar-voz.png",
            ),
        },
        {
            "titulo": "Desactivar vibración",
            "texto": "Desactiva las respuestas con vibración.",
            "qr_img": url_for(
                "cit_citas_turnos.static",
                filename="img/config/paso-04-desactivar-vibracion.png",
            ),
        },
        {
            "titulo": "Activar al acercar un código",
            "texto": "Activa la lectura al acercar un código de barras al lector.",
            "qr_img": url_for(
                "cit_citas_turnos.static",
                filename="img/config/paso-05-activar-al-acercar.png",
            ),
        },
    ]
    total_pasos = len(pasos_config)

    if not 1 <= paso_id <= total_pasos:
        abort(404)

    return render_template(
        "cit_citas_turnos/config.jinja2",
        paso_actual=pasos_config[paso_id - 1],
        paso_num=paso_id,
        total_pasos=total_pasos,
    )

@cit_citas_turnos.route("/cit_citas_turnos/tests", methods=["GET"])
@permission_required(MODULO, Permiso.CREAR)
def tests():
    """Página que en lista las pruebas que se pueden realizar"""

    return render_template("cit_citas_turnos/tests.jinja2")

@cit_citas_turnos.route("/cit_citas_turnos/tests/conexion", methods=["GET"])
@permission_required(MODULO, Permiso.CREAR)
def test_conexion():
    """Prueba de conexión con el sistema de turnos"""

    resultado = True

    if resultado:
        return render_template_string('<span class="text-success"><i class="mdi mdi-check-circle"></i> Todo bien</span>')

    return render_template_string('<span class="text-danger"><i class="mdi mdi-close-circle"></i> Falló</span>')


@cit_citas_turnos.route("/cit_citas_turnos/tests/turno", methods=["GET"])
@permission_required(MODULO, Permiso.CREAR)
def test_turno():
    """Prueba para crear un turno en el sistema de turnos"""

    resultado = False

    if resultado:
        return render_template_string('<span class="text-success"><i class="mdi mdi-check-circle"></i> Todo bien</span>')

    return render_template_string('<span class="text-danger"><i class="mdi mdi-close-circle"></i> Falló</span>')
