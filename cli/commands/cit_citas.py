"""
CLI Commands Cit Citas
"""
import logging

from datetime import date, datetime, time, timedelta

from rich.console import Console
from rich.progress import Progress
from typer import Typer

from pjecz_casiopea_flask.blueprints.cit_citas.models import CitCita, database
from pjecz_casiopea_flask.blueprints.cit_dias_inhabiles.models import CitDiaInhabil
from pjecz_casiopea_flask.blueprints.oficinas.models import Oficina
from pjecz_casiopea_flask.blueprints.usuarios_oficinas.models import UsuarioOficina
from pjecz_casiopea_flask.main import app
from pjecz_casiopea_flask.services.sendmail import PlantillaReporteCitasProximas, Email, MyRequestError

app.app_context().push()

# Configuración del logging
bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
empunadura = logging.FileHandler("logs/cit_citas_enviar_agenda.log", encoding="utf-8")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)


cit_citas = Typer()


@cit_citas.command()
def eliminar(horas: int = 24):
    """Pasa a estatus B las citas pasadas a la fecha de hoy"""
    console = Console()
    # Definir el tiempo límite
    tiempo_limite = datetime.now() - timedelta(hours=horas)
    # Consultar las citas a eliminar (solo activas)
    query_citas = CitCita.query.filter(CitCita.inicio < tiempo_limite, CitCita.estatus == "A")
    total_citas = query_citas.count()

    if total_citas == 0:
        console.print(f"[green]No hay citas para eliminar con más de {horas} horas de antigüedad.[/green]")
        return

    commit_cada = 500

    with Progress(console=console) as progress:
        task = progress.add_task(f"Eliminando {total_citas} citas...", total=total_citas)

        # 1. Obtener solo los IDs para no cargar todos los objetos en memoria.
        #    Se usa with_entities para seleccionar solo la columna 'id'.
        #    .all() aquí es seguro porque solo trae una lista de tuplas de IDs.
        citas_ids = [c[0] for c in query_citas.with_entities(CitCita.id).all()]

        # 2. Procesar los IDs en lotes.
        for i in range(0, total_citas, commit_cada):
            # Seleccionar el lote actual de IDs
            lote_ids = citas_ids[i : i + commit_cada]

            # 3. Ejecutar un UPDATE masivo para el lote actual.
            #    Esto es mucho más eficiente que cargar y modificar cada objeto.
            database.session.query(CitCita).filter(CitCita.id.in_(lote_ids)).update({"estatus": "B"}, synchronize_session=False)

            database.session.commit()
            progress.update(task, advance=len(lote_ids))

    console.print(f"[green]Se han eliminado {total_citas} citas con más de {horas} horas de antigüedad.[/green]")


def _get_proximo_dia_habil() -> date:
    """Obtener el próximo día hábil, saltando fines de semana y días inhábiles"""
    dias_inhabiles = {
        d.fecha
        for d in CitDiaInhabil.query.filter(
            CitDiaInhabil.estatus == "A",
            CitDiaInhabil.fecha >= date.today(),
        ).all()
    }
    candidate = date.today() + timedelta(days=1)
    while True:
        if candidate.weekday() in (5, 6) or candidate in dias_inhabiles:
            candidate += timedelta(days=1)
            continue
        return candidate


@cit_citas.command()
def enviar_agenda():
    """Enviar la agenda del próximo día hábil a los usuarios de cada oficina por SendGrid"""
    console = Console()
    bitacora.info("Inicia la tarea para enviar la agenda del próximo día hábil.")

    # Obtener el próximo día hábil
    proximo_dia_habil = _get_proximo_dia_habil()
    console.print(f"Próximo día hábil: [cyan]{proximo_dia_habil}[/cyan]")
    bitacora.info(f"Próximo día hábil calculado: {proximo_dia_habil}")

    # Límites del día para el filtro de citas
    inicio_dia = datetime.combine(proximo_dia_habil, time.min)
    fin_dia = inicio_dia + timedelta(days=1)

    # Consultar las oficinas activas que pueden agendar citas
    oficinas = Oficina.query.filter(
        Oficina.estatus == "A",
        Oficina.puede_agendar_citas,
    ).all()
    bitacora.info(f"Se encontraron {len(oficinas)} oficinas activas que pueden agendar citas.")

    for oficina in oficinas:
        # Consultar las citas de la oficina para el próximo día hábil
        citas = (
            CitCita.query.filter(
                CitCita.estatus == "A",
                CitCita.estado == "PENDIENTE",
                CitCita.oficina_id == oficina.id,
                CitCita.inicio >= inicio_dia,
                CitCita.inicio < fin_dia,
            )
            .order_by(CitCita.inicio)
            .all()
        )

        # Consultar los usuarios activos asignados a la oficina
        usuarios_oficinas = UsuarioOficina.query.filter(
            UsuarioOficina.estatus == "A",
            UsuarioOficina.oficina_id == oficina.id,
        ).all()
        usuarios = [uo.usuario for uo in usuarios_oficinas if uo.usuario.estatus == "A"]

        if not usuarios:
            msg = f"Oficina '{oficina.clave}' no tiene usuarios activos asignados. Se omite el envío de correo."
            bitacora.warning(msg)
            continue

        usuarios_nombres_str = ", ".join(u.nombre for u in usuarios)
        usuarios_emails_str = ", ".join(u.email for u in usuarios)

        msg = f"Oficina '{oficina.clave}': {len(citas)} citas. Enviando a {len(usuarios)} usuario(s): {usuarios_emails_str}"
        bitacora.info(msg)
        # Creación de la plantilla para el email
        plantilla_reporte_citas_proximas = PlantillaReporteCitasProximas(
            fecha_reporte=proximo_dia_habil,
            usuario_nombre=usuarios_nombres_str,
            oficina=f"{oficina.clave}: {oficina.descripcion_corta}",
            citas=citas,
        )

        # Envío de email
        send_email = Email([u.email for u in usuarios], plantilla_reporte_citas_proximas)
        try:
            send_email.enviar_email()
            bitacora.info(f"Correo para la oficina '{oficina.clave}' enviado correctamente a {usuarios_emails_str}.")
        except MyRequestError as error:
            error_msg = f"Error al enviar email para la oficina '{oficina.clave}' a {usuarios_emails_str}: {error}"
            console.print(f"[red]{error_msg}[/red]")
            bitacora.error(error_msg)

    console.print(f"[green]¡Tarea terminada![/green]")
    bitacora.info("La tarea para enviar la agenda ha finalizado.")
