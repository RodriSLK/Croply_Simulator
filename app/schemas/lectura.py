from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums.enums import TipoSensorEnum


class LecturaSensorSimuladaSchema(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	sensor_id: int
	parcela_id: int
	tipo_sensor: TipoSensorEnum | str
	valor: float
	unidad: str
	timestamp: datetime


class LecturasResponse(BaseModel):
	lecturas: list[LecturaSensorSimuladaSchema]