"""
Cit Categorías, vistas
"""

import json

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_clave, safe_message, safe_string, safe_uuid
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from .forms import CitCategoriaForm
from .models import CitCategoria

MODULO = "CIT CATEGORIAS"

cit_categorias = Blueprint("cit_categorias", __name__, template_folder="templates")


@cit_categorias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cit_categorias.route("/cit_categorias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Cit Categorías"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = CitCategoria.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(CitCategoria.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(CitCategoria.estatus == "A")
    if "clave" in request.form:
        try:
            clave = safe_clave(request.form["clave"])
            if clave != "":
                consulta = consulta.filter(CitCategoria.clave.contains(clave))
        except ValueError:
            pass
    if "nombre" in request.form:
        nombre = safe_string(request.form["nombre"], save_enie=True)
        if nombre != "":
            consulta = consulta.filter(CitCategoria.nombre.contains(nombre))
    # Ordenar y paginar
    registros = consulta.order_by(CitCategoria.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("cit_categorias.detail", cit_categoria_id=resultado.id),
                },
                "nombre": resultado.nombre,
                "toggle_es_activo": {
                    "id": resultado.id,
                    "es_activo": resultado.es_activo,
                    "url": (
                        url_for("cit_categorias.toggle_es_activo_json", cit_categoria_id=resultado.id)
                        if current_user.can_edit(MODULO)
                        else ""
                    ),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@cit_categorias.route("/cit_categorias")
def list_active():
    """Listado de Cit Categorías activas"""
    return render_template(
        "cit_categorias/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Categorías",
        estatus="A",
    )


@cit_categorias.route("/cit_categorias/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Cit Categorías inactivas"""
    return render_template(
        "cit_categorias/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Categorías inactivas",
        estatus="B",
    )


@cit_categorias.route("/cit_categorias/<cit_categoria_id>")
def detail(cit_categoria_id):
    """Detalle de una Cit Categoría"""
    cit_categoria_id = safe_uuid(cit_categoria_id)
    if cit_categoria_id == "":
        abort(400)
    cit_categoria = CitCategoria.query.get_or_404(cit_categoria_id)
    return render_template("cit_categorias/detail.jinja2", cit_categoria=cit_categoria)


@cit_categorias.route("/cit_categorias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Cit Categoría"""
    form = CitCategoriaForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar clave
        clave = safe_clave(form.clave.data)
        if clave == "":
            es_valido = False
            flash("La clave es incorrecta o está vacía", "warning")
        # Validar que la clave sea única
        if CitCategoria.query.filter_by(clave=clave).first():
            es_valido = False
            flash("La clave ya está en uso. Debe de ser único.", "warning")
        # Validar nombre
        nombre = safe_string(form.nombre.data, save_enie=True, max_len=64)
        if nombre == "":
            es_valido = False
            flash("El nombre es incorrecto o está vacío", "warning")
        # Si es válido, guardar
        if es_valido:
            cit_categoria = CitCategoria(clave=clave, nombre=nombre, es_activo=form.es_activo.data)
            cit_categoria.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Categoria {cit_categoria.clave}"),
                url=url_for("cit_categorias.detail", cit_categoria_id=cit_categoria.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("cit_categorias/new.jinja2", form=form)


@cit_categorias.route("/cit_categorias/edicion/<cit_categoria_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(cit_categoria_id):
    """Editar Cit Categoría"""
    cit_categoria_id = safe_uuid(cit_categoria_id)
    if cit_categoria_id == "":
        abort(400)
    cit_categoria = CitCategoria.query.get_or_404(cit_categoria_id)
    form = CitCategoriaForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar clave
        clave = safe_clave(form.clave.data)
        if clave == "":
            es_valido = False
            flash("La clave es incorrecta o está vacía", "warning")
        # Si cambia la clave verificar que no este en uso
        if cit_categoria.clave != clave:
            cit_categoria_existente = CitCategoria.query.filter_by(clave=clave).first()
            if cit_categoria_existente and cit_categoria_existente.id != cit_categoria.id:
                es_valido = False
                flash("La clave ya está en uso. Debe de ser única.", "warning")
        # Validar nombre
        nombre = safe_string(form.nombre.data, save_enie=True, max_len=64)
        if nombre == "":
            es_valido = False
            flash("El nombre es incorrecto o está vacío", "warning")
        # Si es válido, actualizar
        if es_valido:
            cit_categoria.clave = clave
            cit_categoria.nombre = nombre
            cit_categoria.es_activo = form.es_activo.data
            cit_categoria.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Categoria {cit_categoria.clave}"),
                url=url_for("cit_categorias.detail", cit_categoria_id=cit_categoria.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = cit_categoria.clave
    form.nombre.data = cit_categoria.nombre
    form.es_activo.data = cit_categoria.es_activo
    return render_template("cit_categorias/edit.jinja2", form=form, cit_categoria=cit_categoria)


@cit_categorias.route("/cit_categorias/eliminar/<cit_categoria_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(cit_categoria_id):
    """Eliminar Cit Categoría"""
    cit_categoria_id = safe_uuid(cit_categoria_id)
    if cit_categoria_id == "":
        abort(400)
    cit_categoria = CitCategoria.query.get_or_404(cit_categoria_id)
    if cit_categoria.estatus == "A":
        cit_categoria.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada Categoría {cit_categoria.clave}"),
            url=url_for("cit_categorias.detail", cit_categoria_id=cit_categoria.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_categorias.detail", cit_categoria_id=cit_categoria.id))


@cit_categorias.route("/cit_categorias/recuperar/<cit_categoria_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(cit_categoria_id):
    """Recuperar Cit Categoría"""
    cit_categoria_id = safe_uuid(cit_categoria_id)
    if cit_categoria_id == "":
        abort(400)
    cit_categoria = CitCategoria.query.get_or_404(cit_categoria_id)
    if cit_categoria.estatus == "B":
        cit_categoria.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada Categoría {cit_categoria.clave}"),
            url=url_for("cit_categorias.detail", cit_categoria_id=cit_categoria.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_categorias.detail", cit_categoria_id=cit_categoria.id))


@cit_categorias.route("/cit_categorias/toggle_es_activo_json/<cit_categoria_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def toggle_es_activo_json(cit_categoria_id):
    """Cambiar es_activo a su opuesto al dar clic a su boton en datatable"""

    # Consultar
    cit_categoria_id = safe_uuid(cit_categoria_id)
    if cit_categoria_id == "":
        return {"success": False, "message": "No es un UUID válido"}
    cit_categoria = CitCategoria.query.get_or_404(cit_categoria_id)
    if cit_categoria is None:
        return {"success": False, "message": "No encontrado"}

    # Cambiar es_activo a su opuesto y guardar
    cit_categoria.es_activo = not cit_categoria.es_activo
    cit_categoria.save()

    # Entregar JSON
    return {
        "success": True,
        "message": "Activo" if cit_categoria.es_activo == "A" else "Inactivo",
        "es_activo": cit_categoria.es_activo,
        "id": cit_categoria.id,
    }
