from __future__ import annotations

from pydantic import BaseModel

from app.enums.enums import EstadoTransmision
from app.schemas.sensor import SensorEntrada


class ControladorEntrada(BaseModel):
	id: int
	ip: str | None = None
	estado: EstadoTransmision
	sensores: list[SensorEntrada]


class ControladorPatchRequest(BaseModel):
	estado: EstadoTransmision