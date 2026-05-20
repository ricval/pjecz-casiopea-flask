"""
Cit Citas, vistas
"""

import json
from datetime import date, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_email, safe_message, safe_string, safe_uuid
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..cit_clientes.models import CitCliente
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from .models import CitCita
from .forms import CitaAsistenciaForm
from ..usuarios_oficinas.models import UsuarioOficina

MODULO = "CIT CITAS"

cit_citas = Blueprint("cit_citas", __name__, template_folder="templates")


@cit_citas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cit_citas.route("/cit_citas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Cit Citas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = CitCita.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(CitCita.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(CitCita.estatus == "A")
    if "id" in request.form:
        consulta = consulta.filter(CitCita.id == request.form["id"])
    if "fecha_dia" in request.form:
        fecha_dia_ini = request.form["fecha_dia"] + " 00:00:00"
        fecha_dia_fin = request.form["fecha_dia"] + " 23:59:59"
        consulta = consulta.filter(CitCita.inicio >= fecha_dia_ini, CitCita.inicio <= fecha_dia_fin)
    if "cit_cliente_id" in request.form:
        consulta = consulta.filter(CitCita.cit_cliente_id == request.form["cit_cliente_id"])
    if "cit_servicio_id" in request.form:
        consulta = consulta.filter(CitCita.cit_servicio_id == request.form["cit_servicio_id"])
    if "oficina_id" in request.form:
        consulta = consulta.filter(CitCita.oficina_id == request.form["oficina_id"])
    if "estado" in request.form:
        estado = safe_string(request.form["estado"])
        if estado != "":
            consulta = consulta.filter(CitCita.estado == estado)
    # Luego filtrar por columnas de otras tablas
    cit_cliente_email = ""
    if "cit_cliente_email" in request.form:
        cit_cliente_email = safe_email(request.form["cit_cliente_email"], search_fragment=True)
    cit_cliente_nombres = ""
    if "cit_cliente_nombres" in request.form:
        cit_cliente_nombres = safe_string(request.form["cit_cliente_nombres"], save_enie=True)
    cit_cliente_apellido_primero = ""
    if "cit_cliente_apellido_primero" in request.form:
        cit_cliente_apellido_primero = safe_string(request.form["cit_cliente_apellido_primero"], save_enie=True)
    cit_cliente_apellido_segundo = ""
    if "cit_cliente_apellido_segundo" in request.form:
        cit_cliente_apellido_segundo = safe_string(request.form["cit_cliente_apellido_segundo"], save_enie=True)
    if (
        cit_cliente_email != ""
        or cit_cliente_nombres != ""
        or cit_cliente_apellido_primero != ""
        or cit_cliente_apellido_segundo != ""
    ):
        consulta = consulta.join(CitCliente)
        if cit_cliente_email != "":
            consulta = consulta.filter(CitCliente.email.contains(cit_cliente_email))
        if cit_cliente_nombres != "":
            consulta = consulta.filter(CitCliente.nombres.contains(cit_cliente_nombres))
        if cit_cliente_apellido_primero != "":
            consulta = consulta.filter(CitCliente.apellido_primero.contains(cit_cliente_apellido_primero))
        if cit_cliente_apellido_segundo != "":
            consulta = consulta.filter(CitCliente.apellido_segundo.contains(cit_cliente_apellido_segundo))
    # Ordenar y paginar
    registros = consulta.order_by(CitCita.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "fecha": {
                    "fecha": resultado.inicio.strftime("%Y-%m-%d"),
                    "url": url_for("cit_citas.detail", cit_cita_id=resultado.id),
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
                "cit_servicio": {
                    "clave": resultado.cit_servicio.clave,
                    "descripcion": resultado.cit_servicio.descripcion,
                    "url": (
                        url_for("cit_servicios.detail", cit_servicio_id=resultado.cit_servicio.id)
                        if current_user.can_view("CIT SERVICIOS")
                        else ""
                    ),
                },
                "oficina": {
                    "clave": resultado.oficina.clave,
                    "descripcion": resultado.oficina.descripcion,
                    "url": (
                        url_for("oficinas.detail", oficina_id=resultado.oficina.id) if current_user.can_view("OFICINAS") else ""
                    ),
                },
                "inicio": resultado.inicio.strftime("%H:%M"),
                "termino": resultado.termino.strftime("%H:%M"),
                "estado": resultado.estado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@cit_citas.route("/cit_citas/todas")
def list_active():
    """Listado de Cit Citas activas"""

    filtro_oficina = {"estatus": "A"}
    if current_user.can_admin(MODULO) is False:
        usuario_oficina = UsuarioOficina.query.filter_by(usuario=current_user).first()
        filtro_oficina["oficina_id"] = str(usuario_oficina.oficina_id)

    return render_template(
        "cit_citas/list.jinja2",
        filtros=json.dumps(filtro_oficina),
        titulo="Citas (Todas)",
        estatus="A",
        mostrar_btn_hoy=True,
        mostrar_btn_manana=True,
    )


@cit_citas.route("/cit_citas/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Cit Citas inactivas"""
    return render_template(
        "cit_citas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Citas inactivas",
        estatus="B",
    )

@cit_citas.route("/cit_citas")
def list_dia_hoy():
    """Listado de Cit Citas activas del día de hoy"""

    fecha_hoy = date.today().strftime("%Y-%m-%d")
    filtros = {"estatus": "A", "fecha_dia": fecha_hoy}
    if current_user.can_admin(MODULO) is False:
        usuario_oficina = UsuarioOficina.query.filter_by(usuario=current_user).first()
        filtros["oficina_id"] = str(usuario_oficina.oficina_id)

    return render_template(
        "cit_citas/list.jinja2",
        filtros=json.dumps(filtros),
        titulo="Citas para Hoy",
        estatus="A",
        mostrar_btn_todas=True,
        mostrar_btn_manana=True,
    )

@cit_citas.route("/cit_citas/manana")
def list_dia_manana():
    """Listado de Cit Citas activas del día de mañana"""

    fecha_manana = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    filtros = {"estatus": "A", "fecha_dia": fecha_manana}
    if current_user.can_admin(MODULO) is False:
        usuario_oficina = UsuarioOficina.query.filter_by(usuario=current_user).first()
        filtros["oficina_id"] = str(usuario_oficina.oficina_id)

    return render_template(
        "cit_citas/list.jinja2",
        filtros=json.dumps(filtros),
        titulo="Citas para Mañana",
        estatus="A",
        mostrar_btn_todas=True,
        mostrar_btn_hoy=True,
    )


@cit_citas.route("/cit_citas/<cit_cita_id>")
def detail(cit_cita_id):
    """Detalle de un Cit Cita"""
    cit_cita_id = safe_uuid(cit_cita_id)
    if cit_cita_id == "":
        abort(400)
    cit_cita = CitCita.query.get_or_404(cit_cita_id)
    return render_template("cit_citas/detail.jinja2", cit_cita=cit_cita)


@cit_citas.route("/cit_citas/asistencia/<cit_cita_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def asistencia(cit_cita_id):
    """Asistencia de una Cit Cita"""
    cit_cita_id = safe_uuid(cit_cita_id)
    if cit_cita_id == "":
        abort(400)
    cit_cita = CitCita.query.get_or_404(cit_cita_id)
    form = CitaAsistenciaForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar código de asistencia
        codigo_asistencia = safe_string(form.codigo_asistencia.data)
        if codigo_asistencia == "":
            es_valido = False
            flash("El código de asistencia no es válido.", "warning")
        codigo_asistencia_bd = CitCita.query.filter_by(id=cit_cita_id).first()
        if codigo_asistencia != codigo_asistencia_bd.codigo_asistencia:
            es_valido = False
            flash("El código de asistencia no coincide con el esperado.", "warning")
        # Ejecutar cambios en la cita si el código de asistencia es el correcto
        if es_valido:
            cit_cita.estado = "ASISTIO"
            cit_cita.save()
            bitacora = Bitacora(
                    modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                    usuario=current_user,
                    descripcion=safe_message(f"Asistencia añadida a la cita {cit_cita.id}"),
                    url=url_for("cit_citas.detail", cit_cita_id=cit_cita.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    # Carga de valores de campos
    form.id.data = cit_cita.id
    form.cliente_nombre.data = cit_cita.cit_cliente.nombre
    # Entrega del template
    return render_template("cit_citas/asistencia.jinja2", form=form, cit_cita=cit_cita)