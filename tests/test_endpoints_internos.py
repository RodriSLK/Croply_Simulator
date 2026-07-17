from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.enums.enums import EstadoTransmision, TipoSensorEnum
from app.main import app
from app.models.controlador_simulado import ControladorSimulado
from app.models.evento_manual_pendiente import EventoManualPendiente
from app.models.lectura_sensor_simulada import LecturaSensorSimulada
from app.services.alerta_service import reiniciar_estado_alertas
from app.services.scheduler_service import ejecutar_ciclo_simulacion


ENGINE = create_engine("postgresql+psycopg://usuario:password@localhost:5432/croply_simulator")
SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)


def _limpiar_tablas() -> None:
	with ENGINE.begin() as connection:
		connection.execute(
			text("TRUNCATE TABLE lecturas_simuladas, eventos_manuales_pendientes, alertas_simuladas, sensores_simulados, controladores_simulados, parcelas_simuladas RESTART IDENTITY CASCADE")
		)
	reiniciar_estado_alertas()


def _payload_parcela() -> dict[str, object]:
	return {
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
					{"id": 10, "tipo": "TEMP_HUME_AMBIENTAL"},
					{"id": 11, "tipo": "HUMEDAD_SUELO"},
					{"id": 12, "tipo": "RADIACION_SOLAR"},
					{"id": 13, "tipo": "PRECIPITACION"},
					{"id": 14, "tipo": "PH"},
				],
			},
		},
	}


def _crear_parcela(client: TestClient) -> None:
	assert client.post("/parcelas", json=_payload_parcela()).status_code == 201


def _clima_estable(*_args, **_kwargs) -> dict[str, float]:
	return {
		"temperature_2m": 1.0,
		"relative_humidity_2m": 50.0,
		"shortwave_radiation": 600.0,
		"precipitation": 0.4,
		"cloud_cover": 20.0,
		"wind_speed_10m": 3.0,
	}


def test_post_eventos_crea_evento_pendiente() -> None:
	_limpiar_tablas()
	with TestClient(app) as client:
		_crear_parcela(client)
		response = client.post("/parcelas/1/eventos", json={"tipo": "RIEGO", "parametros": {"mm": 20}})

	assert response.status_code == 201

	db = SessionLocal()
	try:
		evento = db.query(EventoManualPendiente).filter(EventoManualPendiente.parcela_id == 1).one()
		assert evento.aplicado is False
		assert evento.tipo_evento.value == "RIEGO"
	finally:
		db.close()


def test_patch_controlador_actualiza_estado() -> None:
	_limpiar_tablas()
	with TestClient(app) as client:
		_crear_parcela(client)
		response = client.patch("/parcelas/1/controlador", json={"estado": "SIN_SEÑAL"})

	assert response.status_code == 200

	db = SessionLocal()
	try:
		controlador = db.query(ControladorSimulado).filter(ControladorSimulado.parcela_id == 1).one()
		assert controlador.estado == EstadoTransmision.SIN_SEÑAL
	finally:
		db.close()


def test_get_lecturas_devuelve_historial_del_scheduler() -> None:
	_limpiar_tablas()
	with TestClient(app) as client:
		_crear_parcela(client)
		with patch("app.services.scheduler_service.obtener_clima_actual", side_effect=_clima_estable):
			ejecutar_ciclo_simulacion()

		response = client.get("/parcelas/1/lecturas")

	assert response.status_code == 200
	body = response.json()
	assert len(body["lecturas"]) == 5
	assert {lectura["sensor_id"] for lectura in body["lecturas"]} == {10, 11, 12, 13, 14}

	db = SessionLocal()
	try:
		assert db.query(LecturaSensorSimulada).filter(LecturaSensorSimulada.parcela_id == 1).count() == 5
	finally:
		db.close()


def test_get_status_devuelve_estructura() -> None:
	_limpiar_tablas()
	with TestClient(app) as client:
		_crear_parcela(client)
		response = client.get("/status")

	assert response.status_code == 200
	body = response.json()
	assert isinstance(body["scheduler_activo"], bool)
	assert body["parcelas_activas"] == 1
	assert set(body.keys()) == {"scheduler_activo", "ultima_ejecucion", "proxima_ejecucion", "parcelas_activas"}