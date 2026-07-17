from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums.enums import TipoSensorEnum


class SensorSimulado(Base):
	__tablename__ = "sensores_simulados"

	sensor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
	controlador_id: Mapped[int] = mapped_column(
		Integer,
		ForeignKey("controladores_simulados.controlador_id", ondelete="CASCADE"),
		nullable=False,
	)
	parcela_id: Mapped[int] = mapped_column(
		Integer,
		ForeignKey("parcelas_simuladas.parcela_id", ondelete="CASCADE"),
		nullable=False,
	)
	tipo: Mapped[TipoSensorEnum] = mapped_column(
		SAEnum(TipoSensorEnum, native_enum=False, length=30),
		nullable=False,
	)
	ip_sensor: Mapped[str | None] = mapped_column(String(45), nullable=True)
	ultimo_valor: Mapped[float | None] = mapped_column(Float, nullable=True)
	fecha_ultima_lectura: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
	vwc_actual: Mapped[float | None] = mapped_column(Float, nullable=True)
	kc: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.4)
	profundidad_radicular: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.4)
	ph_base: Mapped[float | None] = mapped_column(Float, nullable=True, default=6.5)