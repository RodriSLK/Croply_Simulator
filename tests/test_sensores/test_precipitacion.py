from __future__ import annotations

from app.enums.enums import TipoSensorEnum
from app.models.sensor_simulado import SensorSimulado
from app.sensores.precipitacion import calcular_valor


def _sensor() -> SensorSimulado:
	return SensorSimulado(sensor_id=3, controlador_id=1, parcela_id=1, tipo=TipoSensorEnum.PRECIPITACION)


def test_precipitacion_calcula_mm_y_lluvia_efectiva() -> None:
	sensor = _sensor()
	contexto = {}

	valor_sin_evento, unidad = calcular_valor(
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
		contexto,
	)

	contexto_con_evento = {}
	valor_con_evento, _ = calcular_valor(
		{
			"temperature_2m": 24.0,
			"relative_humidity_2m": 65.0,
			"shortwave_radiation": 700.0,
			"precipitation": 12.0,
			"cloud_cover": 20.0,
			"wind_speed_10m": 3.0,
		},
		sensor,
		{"tipo": "LLUVIA", "parametros": {"mm": 20}},
		contexto_con_evento,
	)

	assert unidad == "mm"
	assert valor_sin_evento >= 0
	assert contexto["lluvia_efectiva"] >= 0
	assert valor_con_evento > valor_sin_evento
	assert contexto_con_evento["lluvia_efectiva"] >= contexto["lluvia_efectiva"]