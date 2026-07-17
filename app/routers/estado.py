from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import ParcelaNoEncontradaError
from app.enums.enums import TipoSensorEnum
from app.models.controlador_simulado import ControladorSimulado
from app.models.parcela_simulada import ParcelaSimulada
from app.models.sensor_simulado import SensorSimulado
from app.schemas.parcela import ControladorEstado, ParcelaEstadoResponse, SensorEstado


router = APIRouter()


def _unidad_por_tipo(tipo: TipoSensorEnum) -> str:
	return {
		TipoSensorEnum.TEMP_HUME_AMBIENTAL: "°C",
		TipoSensorEnum.HUMEDAD_SUELO: "%",
		TipoSensorEnum.RADIACION_SOLAR: "W/m²",
		TipoSensorEnum.PRECIPITACION: "mm",
		TipoSensorEnum.PH: "pH",
	}[tipo]


@router.get("/parcelas/{parcela_id}/estado", response_model=ParcelaEstadoResponse)
def obtener_estado_parcela(parcela_id: int, db: Session = Depends(get_db)) -> ParcelaEstadoResponse:
	parcela = db.get(ParcelaSimulada, parcela_id)
	if parcela is None:
		raise ParcelaNoEncontradaError(f"La parcela {parcela_id} no existe")

	controladores = []
	for controlador in db.query(ControladorSimulado).filter(ControladorSimulado.parcela_id == parcela_id).all():
		sensores = []
		for sensor in db.query(SensorSimulado).filter(SensorSimulado.controlador_id == controlador.controlador_id).all():
			sensores.append(
				SensorEstado(
					sensor_id=sensor.sensor_id,
					tipo=sensor.tipo,
					valor_actual=sensor.ultimo_valor,
					unidad=_unidad_por_tipo(sensor.tipo),
					fecha_ultima_lectura=sensor.fecha_ultima_lectura,
				)
			)
		controladores.append(ControladorEstado(controlador_id=controlador.controlador_id, sensores=sensores))

	return ParcelaEstadoResponse(
		parcela_id=parcela.parcela_id,
		nombre=parcela.nombre,
		timestamp_simulacion=datetime.now(timezone.utc),
		controladores=controladores,
	)