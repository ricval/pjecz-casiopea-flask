"""
Cit Oficinas Servicios, modelos
"""

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class CitOficinaServicio(database.Model, UniversalMixin):
    """CitOficinaServicio"""

    # Nombre de la tabla
    __tablename__ = "cit_oficinas_servicios"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Claves foráneas
    cit_servicio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cit_servicios.id"))
    cit_servicio: Mapped["CitServicio"] = relationship(back_populates="cit_oficinas_servicios")
    oficina_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("oficinas.id"))
    oficina: Mapped["Oficina"] = relationship(back_populates="cit_oficinas_servicios")

    # Columnas
    descripcion: Mapped[str] = mapped_column(String(256))
    limite_personas: Mapped[int] = mapped_column(Integer, default=1)
    es_activo: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
        """Representación"""
        return f"<CitOficinaServicio {self.id}>"
