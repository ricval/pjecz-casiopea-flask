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

MODULO = "EXP JUZGADOS"

exp_juzgados = Blueprint("exp_juzgados", __name__, template_folder="templates")


@exp_juzgados.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@exp_juzgados.route("/exp_juzgados/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Exp Juzgado"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ExpJuzgado.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(ExpJuzgado.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(ExpJuzgado.estatus == "A")
    if "clave" in request.form:
        try:
            clave = safe_clave(request.form["clave"])
            if clave != "":
                consulta = consulta.filter(ExpJuzgado.clave.contains(clave))
        except ValueError:
            pass
    if "descripcion_corta" in request.form:
        descripcion_corta = safe_string(request.form["descripcion_corta"], save_enie=True)
        if descripcion_corta != "":
            consulta = consulta.filter(ExpJuzgado.descripcion_corta.contains(descripcion_corta))
    # Ordenar y paginar
    registros = consulta.order_by(ExpJuzgado.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("exp_juzgados.detail", exp_juzgado_id=resultado.id),
                },
                "descripcion_corta": resultado.descripcion_corta,
                "descripcion": resultado.descripcion,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


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


@exp_juzgados.route("/exp_juzgados/<exp_juzgado_id>")
def detail(exp_juzgado_id):
    """Detalle de una Exp Juzgado"""
    exp_juzgado = ExpJuzgado.query.get_or_404(exp_juzgado_id)
    return render_template("exp_juzgados/detail.jinja2", exp_juzgado=exp_juzgado)


@exp_juzgados.route("/exp_juzgados/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Exp Juzgado"""
    form = ExpJuzgadoForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar clave
        clave = safe_clave(form.clave.data)
        if clave == "":
            es_valido = False
            flash("La clave es incorrecta o está vacía", "warning")
        # Validar que la clave sea única
        if ExpJuzgado.query.filter_by(clave=clave).first():
            es_valido = False
            flash("La clave ya está en uso. Debe de ser único.", "warning")
        # Validar descripcion_corta
        descripcion_corta = safe_string(form.descripcion_corta.data, save_enie=True, max_len=64)
        if descripcion_corta == "":
            es_valido = False
            flash("La Descripción corta es incorrecto o está vacía", "warning")
        # Validar descripcion
        descripcion = safe_string(form.descripcion.data, save_enie=True, max_len=256)
        if descripcion == "":
            es_valido = False
            flash("La Descripción corta es incorrecto o está vacía", "warning")
        # Si es válido, guardar
        if es_valido:
            exp_juzgado = ExpJuzgado(
                clave=clave,
                descripcion_corta=descripcion_corta,
                descripcion=descripcion,
            )
            exp_juzgado.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo Juzgado para expedientes {exp_juzgado.clave}"),
                url=url_for("exp_juzgados.detail", exp_juzgado_id=exp_juzgado.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    # Entrega de template
    return render_template("exp_juzgados/new.jinja2", form=form)


@exp_juzgados.route("/exp_juzgados/edicion/<exp_juzgado_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(exp_juzgado_id):
    """Editar Exp Juzgado"""
    exp_juzgado = ExpJuzgado.query.get_or_404(exp_juzgado_id)
    form = ExpJuzgadoForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar clave
        clave = safe_clave(form.clave.data)
        if clave == "":
            es_valido = False
            flash("La clave es incorrecta o está vacía", "warning")
        # Si cambia la clave verificar que no este en uso
        if exp_juzgado.clave != clave:
            exp_juzgado_existente = ExpJuzgado.query.filter_by(clave=clave).first()
            if exp_juzgado_existente and exp_juzgado_existente.id != exp_juzgado.id:
                es_valido = False
                flash("La clave ya está en uso. Debe de ser única.", "warning")
        # Validar descripcion_corta
        descripcion_corta = safe_string(form.descripcion_corta.data, save_enie=True, max_len=64)
        if descripcion_corta == "":
            es_valido = False
            flash("La Descripción Corta es incorrecta o está vacía", "warning")
        # Validar descripcion
        descripcion = safe_string(form.descripcion.data, save_enie=True, max_len=256)
        if descripcion == "":
            es_valido = False
            flash("La Descripción es incorrecta o está vacía", "warning")
        # Si es válido, actualizar
        if es_valido:
            exp_juzgado.clave = clave
            exp_juzgado.descripcion_corta = descripcion_corta
            exp_juzgado.descripcion = form.descripcion.data
            exp_juzgado.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado el juzgado para expedientes {exp_juzgado.clave}"),
                url=url_for("exp_juzgados.detail", exp_juzgado_id=exp_juzgado.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    # Carga de campos
    form.clave.data = exp_juzgado.clave
    form.descripcion_corta.data = exp_juzgado.descripcion_corta
    form.descripcion.data = exp_juzgado.descripcion
    # Entrega de template
    return render_template("exp_juzgados/edit.jinja2", form=form, exp_juzgado=exp_juzgado)


@exp_juzgados.route("/exp_juzgados/eliminar/<exp_juzgado_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(exp_juzgado_id):
    """Eliminar Exp Juzgado"""
    exp_juzgado = ExpJuzgado.query.get_or_404(exp_juzgado_id)
    if exp_juzgado.estatus == "A":
        exp_juzgado.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado el Juzgado para Expedientes {exp_juzgado.clave}"),
            url=url_for("exp_juzgados.detail", exp_juzgado_id=exp_juzgado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("exp_juzgados.detail", exp_juzgado_id=exp_juzgado.id))


@exp_juzgados.route("/exp_juzgados/recuperar/<exp_juzgado_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(exp_juzgado_id):
    """Recuperar Exp Juzgado"""
    exp_juzgado = ExpJuzgado.query.get_or_404(exp_juzgado_id)
    if exp_juzgado.estatus == "B":
        exp_juzgado.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado el Juzgado para Expedientes {exp_juzgado.clave}"),
            url=url_for("exp_juzgados.detail", exp_juzgado_id=exp_juzgado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("exp_juzgados.detail", exp_juzgado_id=exp_juzgado.id))