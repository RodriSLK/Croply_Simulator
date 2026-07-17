from __future__ import annotations

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums.enums import EstadoTransmision


class ControladorSimulado(Base):
	__tablename__ = "controladores_simulados"

	controlador_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
	parcela_id: Mapped[int] = mapped_column(
		Integer,
		ForeignKey("parcelas_simuladas.parcela_id", ondelete="CASCADE"),
		nullable=False,
	)
	ip_controlador: Mapped[str | None] = mapped_column(String(45), nullable=True)
	estado: Mapped[EstadoTransmision] = mapped_column(
		SAEnum(EstadoTransmision, native_enum=False, length=20),
		nullable=False,
		default=EstadoTransmision.TRANSMITIENDO,
	)