from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums.enums import TipoEvento


class EventoManualPendiente(Base):
	__tablename__ = "eventos_manuales_pendientes"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	parcela_id: Mapped[int] = mapped_column(
		Integer,
		ForeignKey("parcelas_simuladas.parcela_id", ondelete="CASCADE"),
		nullable=False,
	)
	tipo_evento: Mapped[TipoEvento] = mapped_column(
		SAEnum(TipoEvento, native_enum=False, length=30),
		nullable=False,
	)
	parametros: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict, server_default="{}")
	aplicado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
	creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)