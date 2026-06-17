"""
Agenda, vistas
"""

from datetime import date, datetime, timedelta

from flask import Blueprint, abort, render_template, url_for
from flask_login import current_user, login_required

from ...lib.safe_string import safe_message, safe_string, safe_uuid
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from ..cit_citas.models import CitCita
from ..cit_clientes.models import CitCliente
from ..usuarios_oficinas.models import UsuarioOficina
from ..cit_oficinas_servicios.models import CitOficinaServicio

MODULO = "AGENDAS"
ESTADOS_VALIDOS = ("PENDIENTE", "ASISTIO", "CANCELO", "INASISTENCIA")

agendas = Blueprint("agendas", __name__, template_folder="templates")


@agendas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@agendas.route("/agendas")
def list_dia_hoy():
    """Listado de la agenda del día de hoy"""

    fecha_hoy = date.today()

    # Buscar que oficina tiene asignado el usuario actual
    usuario_oficina = UsuarioOficina.query.filter_by(usuario=current_user).filter_by(estatus="A").first()
    if not usuario_oficina:
        abort(404)
    oficina = usuario_oficina.oficina

    # Buscar el primer servicio activo de la oficina
    oficina_servicio = CitOficinaServicio.query.filter_by(oficina=oficina).filter_by(estatus="A").first()
    if not oficina_servicio:
        abort(404)
    cit_servicio = oficina_servicio.cit_servicio

    # Determinar horario del servicio; si no tiene, usar el horario de la oficina
    hora_inicio = cit_servicio.desde or oficina.apertura
    hora_fin = cit_servicio.hasta or oficina.cierre
    duracion = cit_servicio.duracion
    duracion_td = timedelta(hours=duracion.hour, minutes=duracion.minute, seconds=duracion.second)

    # Extraer todas las citas de hoy para esta oficina y servicio
    fecha_str = fecha_hoy.strftime("%Y-%m-%d")
    citas = (
        CitCita.query.filter(
            CitCita.inicio >= f"{fecha_str} 00:00:00",
            CitCita.inicio <= f"{fecha_str} 23:59:59",
            CitCita.oficina_id == oficina.id,
            CitCita.cit_servicio_id == cit_servicio.id,
        )
        .join(CitCliente)
        .all()
    )

    # Indexar citas por hora de inicio (sin segundos) para búsqueda rápida
    citas_por_hora = {cita.inicio.replace(second=0, microsecond=0).time(): cita for cita in citas}

    # Generar un renglón por cada slot de duración del servicio
    agenda = []
    slot_dt = datetime.combine(fecha_hoy, hora_inicio)
    fin_dt = datetime.combine(fecha_hoy, hora_fin)
    while slot_dt < fin_dt:
        siguiente_dt = slot_dt + duracion_td
        agenda.append(
            {
                "inicio": slot_dt.time(),
                "termino": siguiente_dt.time(),
                "cita": citas_por_hora.get(slot_dt.time()),
            }
        )
        slot_dt = siguiente_dt

    return render_template(
        "agendas/hoy.jinja2",
        titulo="Agenda de Hoy",
        fecha=fecha_hoy,
        oficina=oficina,
        servicio=cit_servicio,
        agenda=agenda,
    )


@agendas.route("/agendas/cambiar_estado/<cit_cita_id>/<estado>", methods=["POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def cambiar_estado(cit_cita_id, estado):
    """Cambiar el estado de una cita desde la agenda (htmx)"""
    cit_cita_id = safe_uuid(cit_cita_id)
    if cit_cita_id == "":
        abort(400)
    estado = safe_string(estado)
    if estado not in ESTADOS_VALIDOS:
        abort(400)
    cit_cita = CitCita.query.get_or_404(cit_cita_id)
    cit_cita.estado = estado
    cit_cita.save()
    bitacora = Bitacora(
        modulo=Modulo.query.filter_by(nombre=MODULO).first(),
        usuario=current_user,
        descripcion=safe_message(f"Estado cambiado a {estado} en cita {cit_cita.id}"),
        url=url_for("agendas.list_dia_hoy"),
    )
    bitacora.save()
    return render_template("agendas/estado_celda.jinja2", cit_cita=cit_cita)
