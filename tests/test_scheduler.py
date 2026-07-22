from __future__ import annotations

from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.enums.enums import TipoAlerta, TipoEvento, TipoSensorEnum
from app.exceptions import OpenMeteoError
from app.models.alerta_simulada import AlertaSimulada
from app.models.controlador_simulado import ControladorSimulado
from app.models.evento_manual_pendiente import EventoManualPendiente
from app.models.lectura_sensor_simulada import LecturaSensorSimulada
from app.models.parcela_simulada import ParcelaSimulada
from app.models.sensor_simulado import SensorSimulado
from app.schemas.evento import EventoEntrada
from app.services.alerta_service import reiniciar_estado_alertas
from app.services.evento_service import crear_evento_pendiente
from app.services.scheduler_service import ejecutar_ciclo_simulacion, obtener_estado_scheduler


ENGINE = create_engine("postgresql+psycopg://usuario:password@localhost:5432/croply_simulator")
SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)


def _limpiar_tablas() -> None:
	with ENGINE.begin() as connection:
		connection.execute(
			text("TRUNCATE TABLE lecturas_simuladas, eventos_manuales_pendientes, alertas_simuladas, sensores_simulados, controladores_simulados, parcelas_simuladas RESTART IDENTITY CASCADE")
		)
	reiniciar_estado_alertas()


def _crear_parcela(db, parcela_id: int, controlador_id: int, base_latitud: float) -> None:
	db.add(
		ParcelaSimulada(
			parcela_id=parcela_id,
			nombre=f"Parcela {parcela_id}",
			latitud=base_latitud,
			longitud=-68.84,
		)
	)
	db.flush()
	sensores = [
		(100 + parcela_id, TipoSensorEnum.TEMP_HUME_AMBIENTAL),
		(200 + parcela_id, TipoSensorEnum.RADIACION_SOLAR),
		(300 + parcela_id, TipoSensorEnum.PRECIPITACION),
		(400 + parcela_id, TipoSensorEnum.HUMEDAD_SUELO),
		(500 + parcela_id, TipoSensorEnum.PH),
	]
	db.add(
		ControladorSimulado(
			controlador_id=controlador_id,
			parcela_id=parcela_id,
			ip_controlador="192.168.0.10",
		)
	)
	for sensor_id, tipo in sensores:
		db.add(
			SensorSimulado(
				sensor_id=sensor_id,
				controlador_id=controlador_id,
				parcela_id=parcela_id,
				tipo=tipo,
			)
		)
	db.commit()


def _clima_estable(*_args, **_kwargs) -> dict[str, float]:
	return {
		"temperature_2m": 1.0,
		"relative_humidity_2m": 50.0,
		"shortwave_radiation": 600.0,
		"precipitation": 0.4,
		"cloud_cover": 20.0,
		"wind_speed_10m": 3.0,
	}


def _clima_parcialmente_fallido(latitud: float, *_args, **_kwargs) -> dict[str, float]:
	if latitud == -33.5:
		raise OpenMeteoError("fallo simulado")
	return {
		"temperature_2m": 18.0,
		"relative_humidity_2m": 65.0,
		"shortwave_radiation": 500.0,
		"precipitation": 0.2,
		"cloud_cover": 10.0,
		"wind_speed_10m": 4.0,
	}


def test_ciclo_manual_actualiza_sensores_evento_y_alerta() -> None:
	_limpiar_tablas()
	db = SessionLocal()
	try:
		_crear_parcela(db, 1, 10, -32.89)
		evento = crear_evento_pendiente(
			db,
			1,
			EventoEntrada.model_validate({"tipo": "RIEGO", "parametros": {"mm": 20}}),
		)
		assert evento.aplicado is False

		with patch("app.services.scheduler_service.obtener_clima_actual", side_effect=_clima_estable):
			ejecutar_ciclo_simulacion()

		db.expire_all()

		for sensor in db.query(SensorSimulado).filter(SensorSimulado.parcela_id == 1).all():
			assert sensor.ultimo_valor is not None
			assert sensor.fecha_ultima_lectura is not None

		assert db.query(LecturaSensorSimulada).filter(LecturaSensorSimulada.parcela_id == 1).count() == 5
		assert db.query(AlertaSimulada).filter(AlertaSimulada.parcela_id == 1, AlertaSimulada.tipo == TipoAlerta.HELADA).count() == 1
		assert db.get(EventoManualPendiente, evento.id).aplicado is True
		assert obtener_estado_scheduler()["ultima_ejecucion"] is not None
	finally:
		db.close()


def test_ciclo_manual_aisla_fallo_de_openmeteo() -> None:
	_limpiar_tablas()
	db = SessionLocal()
	try:
		_crear_parcela(db, 1, 10, -32.89)
		_crear_parcela(db, 2, 20, -33.5)

		with patch("app.services.scheduler_service.obtener_clima_actual", side_effect=_clima_parcialmente_fallido):
			ejecutar_ciclo_simulacion()

		assert db.query(LecturaSensorSimulada).filter(LecturaSensorSimulada.parcela_id == 1).count() == 5
		assert db.query(LecturaSensorSimulada).filter(LecturaSensorSimulada.parcela_id == 2).count() == 0
		assert db.query(SensorSimulado).filter(SensorSimulado.parcela_id == 2, SensorSimulado.ultimo_valor.isnot(None)).count() == 0
	finally:
		db.close()# Pruebas para scheduler.