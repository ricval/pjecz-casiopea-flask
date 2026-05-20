"""
Expedientes-Juzgados, vistas
"""

import json

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_clave, safe_message, safe_string
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from .forms import ExpJuzgadoForm
from .models import ExpJuzgado

MODULO = "EXP_JUZGADOS"

exp_juzgados = Blueprint("exp_juzgados", __name__, template_folder="templates")


@exp_juzgados.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@exp_juzgados.route("/exp_juzgados")
def list_active():
    """Listado de Expedientes-Juzgados activos"""
    return render_template(
        "exp_juzgados/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Juzgados",
        estatus="A",
    )

@exp_juzgados.route("/exp_juzgados/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Expedientes-Juzgados inactivos"""
    return render_template(
        "exp_juzgados/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Juzgados inactivos",
        estatus="B",
    )