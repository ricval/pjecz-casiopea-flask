"""
Cit Citas Turnos, vistas
"""

from datetime import date, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.safe_string import safe_email, safe_message, safe_string, safe_uuid
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..cit_clientes.models import CitCliente
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from ..cit_citas.models import CitCita

MODULO = "CIT CITAS TURNOS"

cit_citas_turnos = Blueprint("cit_citas_turnos", __name__, template_folder="templates")


@cit_citas_turnos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cit_citas_turnos.route("/cit_citas_turnos", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def crear_turno():
    """Creación del turno en el sistema de turnos"""

    if "barcode" in request.form:
        codigo_barras = request.form["barcode"]
        cit_cita = CitCita.query.filter_by(codigo_barras=codigo_barras).first()
        if cit_cita:
            return render_template("cit_citas_turnos/captura.jinja2", cit_cita=cit_cita)
        else:
            return render_template("cit_citas_turnos/captura.jinja2", error=True)

    return render_template("cit_citas_turnos/captura.jinja2")