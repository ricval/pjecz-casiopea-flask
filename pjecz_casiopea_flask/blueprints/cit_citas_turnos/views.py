"""
Cit Citas Turnos, vistas
"""

from typing import Tuple

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