"""
CLI Commands Cit Clientes Clientes
"""
import logging
from rich.console import Console
from rich.progress import Progress
from typer import Typer

from pjecz_casiopea_flask.blueprints.cit_clientes_registros.models import CitClienteRegistro
from pjecz_casiopea_flask.main import app, database

app.app_context().push()

# Configuración del logging
bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
empunadura = logging.FileHandler("logs/cit_clientes_registros_eliminar.log", encoding="utf-8")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

cit_clientes_registros = Typer()


@cit_clientes_registros.command()
def eliminar():
    """Eliminar registros de clientes que no fueron completadas."""
    console = Console()
    bitacora.info("Inicia la tarea para eliminar registros no completadas.")
    console.print("Eliminando registros que NO fueron completadas...")

    # Consultar registros con estatus 'A'
    query = CitClienteRegistro.query.filter_by(estatus="A")
    total_registros = query.count()

    # Si no hay registros que eliminar, mostrar mensaje y salir
    if total_registros == 0:
        msg = "No se encontraron registros pendientes para eliminar."
        console.print(f"[green]{msg}[/green]")
        bitacora.info(msg)
        return

    commit_cada = 100

    # Eliminar registros
    with Progress(console=console) as progress:
        task = progress.add_task(f"Eliminando {total_registros} registros...", total=total_registros)

        # Obtener solo los IDs para no cargar todos los objetos en memoria
        registros_ids = [r[0] for r in query.with_entities(CitClienteRegistro.id).all()]

        # Procesar los IDs en lotes
        for i in range(0, total_registros, commit_cada):
            lote_ids = registros_ids[i : i + commit_cada]

            # Ejecutar un UPDATE masivo para el lote actual (borrado lógico)
            database.session.query(CitClienteRegistro).filter(CitClienteRegistro.id.in_(lote_ids)).update({"estatus": "B"}, synchronize_session=False)
            database.session.commit()
            progress.update(task, advance=len(lote_ids))

    # Mensaje final
    msg = f"Se eliminaron {total_registros} registros pendientes."
    console.print(f"[green]{msg}[/green]")
    bitacora.info(msg)
    bitacora.info("La tarea ha finalizado.")