from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums.enums import EstadoTransmision, TipoSensorEnum


class SensorEntrada(BaseModel):
	id: int
	tipo: TipoSensorEnum


class ControladorEntrada(BaseModel):
	id: int
	ip: str | None = None
	estado: EstadoTransmision
	sensores: list[SensorEntrada]


class ParcelaEntrada(BaseModel):
	id: int
	nombre: str
	latitud: float
	longitud: float
	controlador: ControladorEntrada


class ParcelaRequest(BaseModel):
	parcela: ParcelaEntrada


class SensorEstado(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	sensor_id: int
	tipo: TipoSensorEnum
	valor_actual: float | None = None
	unidad: str | None = None
	fecha_ultima_lectura: datetime | None = None


class ControladorEstado(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	controlador_id: int
	sensores: list[SensorEstado]


class ParcelaEstadoResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	parcela_id: int
	nombre: str
	timestamp_simulacion: datetime | None = None
	controladores: list[ControladorEstado]