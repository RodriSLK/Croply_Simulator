from __future__ import annotations

import random

from app.enums.enums import TipoSensorEnum
from app.models.sensor_simulado import SensorSimulado
from app.sensores.radiacion_solar import calcular_valor


def _sensor() -> SensorSimulado:
	return SensorSimulado(sensor_id=2, controlador_id=1, parcela_id=1, tipo=TipoSensorEnum.RADIACION_SOLAR)


def test_radiacion_solar_calcula_valor_y_eto() -> None:
	random.seed(2)
	sensor = _sensor()
	contexto = {"temperatura": 25.0}

	valor, unidad = calcular_valor(
		{
			"temperature_2m": 24.0,
			"relative_humidity_2m": 65.0,
			"shortwave_radiation": 700.0,
			"precipitation": 0.0,
			"cloud_cover": 20.0,
			"wind_speed_10m": 3.0,
		},
		sensor,
		None,
		contexto,
	)

	assert unidad == "W/m²"
	assert valor > 0
	assert contexto["ETo"] >= 0