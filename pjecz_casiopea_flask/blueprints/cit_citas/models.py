"""
Cit Citas, modelos
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import BYTEA, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config.extensions import database
from ...lib.universal_mixin import UniversalMixin


class CitCita(database.Model, UniversalMixin):
    """CitCita"""

    ESTADOS = {
        "ASISTIO": "Asistió",
        "CANCELO": "Canceló",
        "INASISTENCIA": "Inasistencia",
        "PENDIENTE": "Pendiente",
    }

    # Nombre de la tabla
    __tablename__ = "cit_citas"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Claves foráneas
    cit_cliente_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cit_clientes.id"))
    cit_cliente: Mapped["CitCliente"] = relationship(back_populates="cit_citas")
    cit_servicio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cit_servicios.id"))
    cit_servicio: Mapped["CitServicio"] = relationship(back_populates="cit_citas")
    oficina_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("oficinas.id"))
    oficina: Mapped["Oficina"] = relationship(back_populates="cit_citas")

    # Columnas
    inicio: Mapped[datetime]
    termino: Mapped[datetime]
    notas: Mapped[Optional[str]] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(Enum(*ESTADOS, name="estados", native_enum=False), index=True)
    cancelar_antes: Mapped[Optional[datetime]]
    asistencia: Mapped[bool] = mapped_column(default=False)
    codigo_asistencia: Mapped[Optional[str]] = mapped_column(String(6), default="000000")
    codigo_acceso_id: Mapped[Optional[int]]
    # codigo_acceso_imagen: Mapped[Optional[bytes]] = mapped_column(BYTEA)
    codigo_acceso_url: Mapped[Optional[str]] = mapped_column(String(512))

    # Para controlar la migracion desde pjecz_citas_v2 se incluye el id_original
    id_original: Mapped[Optional[int]] = mapped_column(index=True)

    def __repr__(self):
        """Representación"""
        return f"<CitCita {self.id}>"
