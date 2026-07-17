from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ParcelaSimulada(Base):
	__tablename__ = "parcelas_simuladas"

	parcela_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
	nombre: Mapped[str] = mapped_column(String(255), nullable=False)
	latitud: Mapped[float] = mapped_column(Float, nullable=False)
	longitud: Mapped[float] = mapped_column(Float, nullable=False)
	activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
	creada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)