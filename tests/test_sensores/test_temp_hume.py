from __future__ import annotations

import random

from app.enums.enums import TipoSensorEnum
from app.models.sensor_simulado import SensorSimulado
from app.sensores.temp_hume_ambiental import calcular_valor


def _sensor() -> SensorSimulado:
	return SensorSimulado(sensor_id=1, controlador_id=1, parcela_id=1, tipo=TipoSensorEnum.TEMP_HUME_AMBIENTAL)


def test_temp_hume_calcula_valor_y_contexto_en_rango() -> None:
	random.seed(1)
	sensor = _sensor()
	contexto: dict = {}

	valor, unidad = calcular_valor(
		{
			"temperature_2m": 24.0,
			"relative_humidity_2m": 65.0,
			"shortwave_radiation": 500.0,
			"precipitation": 0.0,
			"cloud_cover": 30.0,
			"wind_speed_10m": 3.0,
		},
		sensor,
		None,
		contexto,
	)

	assert unidad == "°C"
	assert -50 <= valor <= 60
	assert 0 <= contexto["humedad_relativa"] <= 100
	assert contexto["VPD"] >= 0


def test_temp_hume_evento_helada_resta_dos_grados() -> None:
	sensor = _sensor()
	sensor.ultimo_valor = 20.0

	valor, unidad = calcular_valor(
		{
			"temperature_2m": 24.0,
			"relative_humidity_2m": 65.0,
			"shortwave_radiation": 500.0,
			"precipitation": 0.0,
			"cloud_cover": 30.0,
			"wind_speed_10m": 3.0,
		},
		sensor,
		{"tipo": "HELADA", "parametros": {}},
		{},
	)

	assert unidad == "°C"
	assert valor == 18.0