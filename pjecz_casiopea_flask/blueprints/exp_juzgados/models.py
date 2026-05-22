"""
Expedientes-Juzgados
"""

from typing import List

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class ExpJuzgado(database.Model, UniversalMixin):
    """
    Listado de juzgados de los cuales se pueden pedir expedientes en el
    servicio "Revisión de Expedientes" de la unidad "Archivo"
    """

    # Nombre de la tabla
    __tablename__ = "exp_juzgados"

    # Clave primaria
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    descripcion_corta: Mapped[str] = mapped_column(String(64))
    descripcion: Mapped[str] = mapped_column(String(256))

    def __repr__(self):
        """Representación"""
        return f"<Juzgado {self.clave}>"
