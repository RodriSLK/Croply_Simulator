from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.exceptions import ParcelaNoEncontradaError, ParcelaYaExisteError
from app.models.alerta_simulada import AlertaSimulada
from app.models.controlador_simulado import ControladorSimulado
from app.models.evento_manual_pendiente import EventoManualPendiente
from app.models.lectura_sensor_simulada import LecturaSensorSimulada
from app.models.parcela_simulada import ParcelaSimulada
from app.models.sensor_simulado import SensorSimulado
from app.schemas.parcela import ParcelaRequest
from app.services.parcela_service import crear_parcela, eliminar_parcela, reemplazar_configuracion


ENGINE = create_engine("postgresql+psycopg://usuario:password@localhost:5432/croply_simulator")
SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def limpiar_tablas() -> None:
	with ENGINE.begin() as connection:
		connection.execute(text("TRUNCATE TABLE lecturas_simuladas, eventos_manuales_pendientes, alertas_simuladas, sensores_simulados, controladores_simulados, parcelas_simuladas RESTART IDENTITY CASCADE"))


def _dto(sensor_ids: list[int] | None = None) -> ParcelaRequest:
	sensor_ids = sensor_ids or [10, 11, 12, 13, 14]
	return ParcelaRequest.model_validate(
		{
			"parcela": {
				"id": 1,
				"nombre": "Parcela Norte",
				"latitud": -32.89,
				"longitud": -68.84,
				"controlador": {
					"id": 3,
					"ip": "192.168.0.10",
					"estado": "TRANSMITIENDO",
					"sensores": [
						{"id": sensor_ids[0], "tipo": "TEMP_HUME_AMBIENTAL"},
						{"id": sensor_ids[1], "tipo": "HUMEDAD_SUELO"},
						{"id": sensor_ids[2], "tipo": "RADIACION_SOLAR"},
						{"id": sensor_ids[3], "tipo": "PRECIPITACION"},
						{"id": sensor_ids[4], "tipo": "PH"},
					],
				},
			}
		}
	)


def test_crear_parcela_puebla_tablas() -> None:
	db = SessionLocal()
	try:
		crear_parcela(db, _dto())

		assert db.get(ParcelaSimulada, 1) is not None
		assert db.get(ControladorSimulado, 3) is not None
		assert db.query(SensorSimulado).filter(SensorSimulado.parcela_id == 1).count() == 5
	finally:
		db.close()


def test_crear_parcela_duplicada_lanza_error() -> None:
	db = SessionLocal()
	try:
		dto = _dto()
		crear_parcela(db, dto)

		with pytest.raises(ParcelaYaExisteError):
			crear_parcela(db, dto)
	finally:
		db.close()


def test_reemplazar_configuracion_elimina_sensor_y_historico() -> None:
	db = SessionLocal()
	try:
		crear_parcela(db, _dto())
		db.add(
			LecturaSensorSimulada(
				sensor_id=14,
				parcela_id=1,
				tipo_sensor="PH",
				valor=6.7,
				unidad="pH",
			)
		)
		db.commit()

		reemplazar_configuracion(db, 1, _dto([10, 11, 12, 13, 15]))

		assert db.get(SensorSimulado, 14) is None
		assert db.query(LecturaSensorSimulada).filter(LecturaSensorSimulada.sensor_id == 14).count() == 0
		assert db.get(SensorSimulado, 15) is not None
	finally:
		db.close()


def test_reemplazar_parcela_inexistente_lanza_error() -> None:
	db = SessionLocal()
	try:
		with pytest.raises(ParcelaNoEncontradaError):
			reemplazar_configuracion(db, 1, _dto())
	finally:
		db.close()


def test_eliminar_parcela_borra_dependencias() -> None:
	db = SessionLocal()
	try:
		crear_parcela(db, _dto())
		db.add(
			LecturaSensorSimulada(
				sensor_id=10,
				parcela_id=1,
				tipo_sensor="TEMP_HUME_AMBIENTAL",
				valor=23.4,
				unidad="°C",
			)
		)
		db.commit()

		eliminar_parcela(db, 1)

		assert db.get(ParcelaSimulada, 1) is None
		assert db.query(ControladorSimulado).filter(ControladorSimulado.parcela_id == 1).count() == 0
		assert db.query(SensorSimulado).filter(SensorSimulado.parcela_id == 1).count() == 0
		assert db.query(LecturaSensorSimulada).filter(LecturaSensorSimulada.parcela_id == 1).count() == 0
		assert db.query(AlertaSimulada).filter(AlertaSimulada.parcela_id == 1).count() == 0
		assert db.query(EventoManualPendiente).filter(EventoManualPendiente.parcela_id == 1).count() == 0
	finally:
		db.close()


def test_eliminar_parcela_inexistente_lanza_error() -> None:
	db = SessionLocal()
	try:
		with pytest.raises(ParcelaNoEncontradaError):
			eliminar_parcela(db, 1)
	finally:
		db.close()