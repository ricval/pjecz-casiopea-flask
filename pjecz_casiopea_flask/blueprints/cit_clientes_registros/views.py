"""
Cit Clientes Registros, vistas
"""

import json

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from sqlalchemy import or_

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_email, safe_message, safe_string, safe_uuid
from ...config.settings import get_settings
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from ..cit_clientes.models import CitCliente
from .models import CitClienteRegistro


MODULO = "CIT CLIENTES REGISTROS"

cit_clientes_registros = Blueprint("cit_clientes_registros", __name__, template_folder="templates")


@cit_clientes_registros.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cit_clientes_registros.route("/cit_clientes_registros/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Cit Clientes Registros"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = CitClienteRegistro.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(CitClienteRegistro.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(CitClienteRegistro.estatus == "A")
    # Luego filtrar por columnas de otras tablas
    if "email" in request.form:
        cit_cliente_email = safe_email(request.form["email"], search_fragment=True)
        if cit_cliente_email:
            consulta = consulta.filter(CitClienteRegistro.email.contains(cit_cliente_email))
    elif "nombre_completo" in request.form:
        cit_cliente_nombre_completo = safe_string(request.form["nombre_completo"], save_enie=True)
        if cit_cliente_nombre_completo:
            palabras = cit_cliente_nombre_completo.split()
        palabras = cit_cliente_nombre_completo.split()
        for palabra in palabras:
            consulta = consulta.filter(
                or_(CitClienteRegistro.nombres.contains(palabra),
                    CitClienteRegistro.apellido_primero.contains(palabra),
                    CitClienteRegistro.apellido_segundo.contains(palabra)
                    ))
    # Ordenar y paginar
    registros = consulta.order_by(CitClienteRegistro.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "creado": resultado.creado.strftime("%Y-%m-%d %H:%M"),
                    "url": url_for("cit_clientes_registros.detail", cit_cliente_registro_id=resultado.id),
                },
                "email": resultado.email,
                "nombre_completo": resultado.nombre,
                "expiracion": resultado.expiracion.strftime("%Y-%m-%dT%H:%M:%S"),
                "ya_registrado": resultado.ya_registrado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@cit_clientes_registros.route("/cit_clientes_registros")
def list_active():
    """Listado de Cit Clientes Regsitros activos"""
    return render_template(
        "cit_clientes_registros/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Clientes Registros",
        estatus="A",
    )


@cit_clientes_registros.route("/cit_clientes_registros/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Cit Clientes Registros inactivos"""
    return render_template(
        "cit_clientes_registros/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Clientes Registros inactivos",
        estatus="B",
    )


@cit_clientes_registros.route("/cit_clientes_registros/<cit_cliente_registro_id>")
def detail(cit_cliente_registro_id):
    """Detalle de un Cit Cliente Registro"""
    cit_cliente_registro_id = safe_uuid(cit_cliente_registro_id)
    if cit_cliente_registro_id == "":
        abort(400)
    cit_cliente_registro = CitClienteRegistro.query.get_or_404(cit_cliente_registro_id)
    # Elaborar el URL de verificación
    settings = get_settings()
    verificacion_url = settings.NEW_ACCOUNT_CONFIRM_URL
    verificacion_url = f"{verificacion_url}?id={str(cit_cliente_registro.id)}"
    verificacion_url = f"{verificacion_url}&cadena_validar={cit_cliente_registro.cadena_validar}"
    return render_template("cit_clientes_registros/detail.jinja2", cit_cliente_registro=cit_cliente_registro, verificacion_url=verificacion_url)


@cit_clientes_registros.route("/cit_clientes_registros/eliminar/<cit_cliente_registro_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(cit_cliente_registro_id):
    """Eliminar un Cit Cliente Registro"""
    cit_cliente_registro_id = safe_uuid(cit_cliente_registro_id)
    if cit_cliente_registro_id == "":
        abort(400)
    cit_cliente_registro = CitClienteRegistro.query.get_or_404(cit_cliente_registro_id)
    if cit_cliente_registro.estatus == "A":
        cit_cliente_registro.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Intento de Registro de un Cliente {cit_cliente_registro.email}"),
            url=url_for("cit_clientes_registros.detail", cit_cliente_registro_id=cit_cliente_registro.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_clientes_registros.detail", cit_cliente_registro_id=cit_cliente_registro.id))