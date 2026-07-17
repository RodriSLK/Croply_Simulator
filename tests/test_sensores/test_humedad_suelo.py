from __future__ import annotations

from app.enums.enums import TipoSensorEnum
from app.models.sensor_simulado import SensorSimulado
from app.sensores.humedad_suelo import calcular_valor


def _sensor() -> SensorSimulado:
	return SensorSimulado(
		sensor_id=4,
		controlador_id=1,
		parcela_id=1,
		tipo=TipoSensorEnum.HUMEDAD_SUELO,
		vwc_actual=None,
		kc=0.4,
		profundidad_radicular=0.4,
	)


def test_humedad_suelo_persiste_vwc_actual() -> None:
	sensor = _sensor()
	contexto = {"ETo": 5.0, "lluvia_efectiva": 1.0}

	primer_valor, unidad = calcular_valor(
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

	segundo_valor, _ = calcular_valor(
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

	assert unidad == "%"
	assert 0 <= primer_valor <= 100
	assert sensor.vwc_actual == segundo_valor
	assert segundo_valor >= 0


def test_humedad_suelo_evento_riego_incrementa_vwc() -> None:
	sensor = _sensor()
	contexto = {"ETo": 5.0, "lluvia_efectiva": 1.0}

	valor_sin_evento, _ = calcular_valor(
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

	sensor.vwc_actual = None
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
		{"tipo": "RIEGO", "parametros": {"mm": 20}},
		{"ETo": 5.0, "lluvia_efectiva": 1.0},
	)

	assert valor_con_evento > valor_sin_evento