from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums.enums import TipoSensorEnum


class SensorEntrada(BaseModel):
	id: int
	tipo: TipoSensorEnum


class SensorEstado(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	sensor_id: int
	tipo: TipoSensorEnum
	valor_actual: float | None = None
	unidad: str | None = None
	fecha_ultima_lectura: datetime | None = None
