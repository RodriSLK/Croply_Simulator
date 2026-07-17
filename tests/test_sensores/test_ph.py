from __future__ import annotations

from datetime import datetime, timedelta, timezone
import random

from app.enums.enums import TipoSensorEnum
from app.models.sensor_simulado import SensorSimulado
from app.sensores.ph import calcular_valor


def _sensor() -> SensorSimulado:
	return SensorSimulado(
		sensor_id=5,
		controlador_id=1,
		parcela_id=1,
		tipo=TipoSensorEnum.PH,
		ph_base=6.5,
		fecha_ultima_lectura=datetime.now(timezone.utc) - timedelta(days=12),
	)


def test_ph_calcula_valor_en_rango() -> None:
	random.seed(5)
	sensor = _sensor()

	valor, unidad = calcular_valor(
		{
			"temperature_2m": 24.0,
			"relative_humidity_2m": 65.0,
			"shortwave_radiation": 700.0,
			"precipitation": 12.0,
			"cloud_cover": 20.0,
			"wind_speed_10m": 3.0,
		},
		sensor,
		None,
		{},
	)

	assert unidad == "pH"
	assert 0 <= valor <= 14