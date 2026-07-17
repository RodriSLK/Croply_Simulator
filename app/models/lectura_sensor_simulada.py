from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LecturaSensorSimulada(Base):
	__tablename__ = "lecturas_simuladas"

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	sensor_id: Mapped[int] = mapped_column(
		Integer,
		ForeignKey("sensores_simulados.sensor_id", ondelete="CASCADE"),
		nullable=False,
	)
	parcela_id: Mapped[int] = mapped_column(
		Integer,
		ForeignKey("parcelas_simuladas.parcela_id", ondelete="CASCADE"),
		nullable=False,
	)
	tipo_sensor: Mapped[str] = mapped_column(String(30), nullable=False)
	valor: Mapped[float] = mapped_column(Float, nullable=False)
	unidad: Mapped[str] = mapped_column(String(20), nullable=False)
	timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)