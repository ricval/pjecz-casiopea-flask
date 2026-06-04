"""
Cit Clientes Recuperaciones, vistas
"""

import json

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from sqlalchemy import or_

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_email, safe_message, safe_string, safe_uuid
from ...config.settings import get_settings
from ..bitacoras.models import Bitacora
from ..cit_clientes.models import CitCliente
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from .models import CitClienteRecuperacion

MODULO = "CIT CLIENTES RECUPERACIONES"

cit_clientes_recuperaciones = Blueprint("cit_clientes_recuperaciones", __name__, template_folder="templates")


@cit_clientes_recuperaciones.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cit_clientes_recuperaciones.route("/cit_clientes_recuperaciones/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Cit Clientes Recuperaciones"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = CitClienteRecuperacion.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(CitClienteRecuperacion.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(CitClienteRecuperacion.estatus == "A")
    # Luego filtrar por columnas de otras tablas
    if "email" in request.form:
        cit_cliente_email = safe_email(request.form["email"], search_fragment=True)
        if cit_cliente_email:
            consulta = consulta.join(CitCliente)
            consulta = consulta.filter(CitCliente.email.contains(cit_cliente_email))
    elif "nombre_completo" in request.form:
        cit_cliente_nombre_completo = safe_string(request.form["nombre_completo"], save_enie=True)
        if cit_cliente_nombre_completo:
            consulta = consulta.join(CitCliente)
            palabras = cit_cliente_nombre_completo.split()
        palabras = cit_cliente_nombre_completo.split()
        for palabra in palabras:
            consulta = consulta.filter(
                or_(CitCliente.nombres.contains(palabra),
                    CitCliente.apellido_primero.contains(palabra),
                    CitCliente.apellido_segundo.contains(palabra)
                    ))
    # Ordenar y paginar
    registros = consulta.order_by(CitClienteRecuperacion.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "creado": resultado.creado.strftime("%Y-%m-%d %H:%M"),
                    "url": url_for("cit_clientes_recuperaciones.detail", cit_cliente_recuperacion_id=resultado.id),
                },
                "cit_cliente": {
                    "email": resultado.cit_cliente.email,
                    "url": (
                        url_for("cit_clientes.detail", cit_cliente_id=resultado.cit_cliente.id)
                        if current_user.can_view("CIT CLIENTES")
                        else ""
                    ),
                },
                "cit_cliente_nombre": resultado.cit_cliente.nombre,
                "expiracion": resultado.expiracion.strftime("%Y-%m-%dT%H:%M:%S"),
                "ya_recuperado": resultado.ya_recuperado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@cit_clientes_recuperaciones.route("/cit_clientes_recuperaciones")
def list_active():
    """Listado de Cit Clientes Recuperaciones activas"""
    return render_template(
        "cit_clientes_recuperaciones/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Clientes Recuperaciones",
        estatus="A",
    )


@cit_clientes_recuperaciones.route("/cit_clientes_recuperaciones/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Cit Clientes Recuperaciones inactivas"""
    return render_template(
        "cit_clientes_recuperaciones/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Clientes Recuperaciones inactivos",
        estatus="B",
    )


@cit_clientes_recuperaciones.route("/cit_clientes_recuperaciones/<cit_cliente_recuperacion_id>")
def detail(cit_cliente_recuperacion_id):
    """Detalle de un Cit Cliente Recuperacion"""
    cit_cliente_recuperacion_id = safe_uuid(cit_cliente_recuperacion_id)
    if cit_cliente_recuperacion_id == "":
        abort(400)
    cit_cliente_recuperacion = CitClienteRecuperacion.query.get_or_404(cit_cliente_recuperacion_id)
    # Elaborar el URL de verificación
    settings = get_settings()
    recuperacion_url = settings.RECOVER_ACCOUNT_CONFIRM_URL
    recuperacion_url = f"{recuperacion_url}?id={str(cit_cliente_recuperacion.id)}"
    recuperacion_url = f"{recuperacion_url}&cadena_validar={cit_cliente_recuperacion.cadena_validar}"
    return render_template("cit_clientes_recuperaciones/detail.jinja2", cit_cliente_recuperacion=cit_cliente_recuperacion, recuperacion_url=recuperacion_url)


@cit_clientes_recuperaciones.route("/cit_clientes_recuperaciones/eliminar/<cit_cliente_recuperacion_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(cit_cliente_recuperacion_id):
    """Eliminar un Cit Cliente Recuperacion"""
    cit_cliente_recuperacion_id = safe_uuid(cit_cliente_recuperacion_id)
    if cit_cliente_recuperacion_id == "":
        abort(400)
    cit_cliente_recuperacion = CitClienteRecuperacion.query.get_or_404(cit_cliente_recuperacion_id)
    if cit_cliente_recuperacion.estatus == "A":
        cit_cliente_recuperacion.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Intento de Recuperación de contraseña de un Cliente {cit_cliente_recuperacion.cit_cliente.email}"),
            url=url_for("cit_clientes_recuperaciones.detail", cit_cliente_recuperacion_id=cit_cliente_recuperacion.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_clientes_recuperaciones.detail", cit_cliente_recuperacion_id=cit_cliente_recuperacion.id))