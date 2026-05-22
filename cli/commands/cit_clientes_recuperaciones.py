"""
CLI Commands Cit Clientes Recuperaciones
"""
import logging
from rich.console import Console
from rich.progress import Progress
from typer import Typer

from pjecz_casiopea_flask.blueprints.cit_clientes_recuperaciones.models import CitClienteRecuperacion
from pjecz_casiopea_flask.main import app, database

app.app_context().push()

# Configuración del logging
bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
empunadura = logging.FileHandler("logs/cit_clientes_recuperaciones_eliminar.log", encoding="utf-8")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

cit_clientes_recuperaciones = Typer()


@cit_clientes_recuperaciones.command()
def eliminar():
    """Eliminar recuperaciones de contraseña que no fueron completadas."""
    console = Console()
    bitacora.info("Inicia la tarea para eliminar recuperaciones de contraseña no completadas.")
    console.print("Eliminando recuperaciones de contraseña que NO fueron completadas...")

    # Consultar recuperaciones con estatus 'A'
    query = CitClienteRecuperacion.query.filter_by(estatus="A")
    total_recuperaciones = query.count()

    # Si no hay recuperaciones que eliminar, mostrar mensaje y salir
    if total_recuperaciones == 0:
        msg = "No se encontraron recuperaciones pendientes para eliminar."
        console.print(f"[green]{msg}[/green]")
        bitacora.info(msg)
        return

    commit_cada = 100

    # Eliminar recuperaciones
    with Progress(console=console) as progress:
        task = progress.add_task(f"Eliminando {total_recuperaciones} recuperaciones...", total=total_recuperaciones)

        # Obtener solo los IDs para no cargar todos los objetos en memoria
        recuperaciones_ids = [r[0] for r in query.with_entities(CitClienteRecuperacion.id).all()]

        # Procesar los IDs en lotes
        for i in range(0, total_recuperaciones, commit_cada):
            lote_ids = recuperaciones_ids[i : i + commit_cada]

            # Ejecutar un UPDATE masivo para el lote actual (borrado lógico)
            database.session.query(CitClienteRecuperacion).filter(CitClienteRecuperacion.id.in_(lote_ids)).update({"estatus": "B"}, synchronize_session=False)
            database.session.commit()
            progress.update(task, advance=len(lote_ids))

    # Mensaje final
    msg = f"Se eliminaron {total_recuperaciones} recuperaciones pendientes."
    console.print(f"[green]{msg}[/green]")
    bitacora.info(msg)
    bitacora.info("La tarea ha finalizado.")