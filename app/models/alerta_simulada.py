from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums.enums import TipoAlerta


class AlertaSimulada(Base):
	__tablename__ = "alertas_simuladas"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	parcela_id: Mapped[int] = mapped_column(
		Integer,
		ForeignKey("parcelas_simuladas.parcela_id", ondelete="CASCADE"),
		nullable=False,
	)
	tipo: Mapped[TipoAlerta] = mapped_column(
		SAEnum(TipoAlerta, native_enum=False, length=30),
		nullable=False,
	)
	valor_disparador: Mapped[float] = mapped_column(Float, nullable=False)
	resuelta: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
	timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)