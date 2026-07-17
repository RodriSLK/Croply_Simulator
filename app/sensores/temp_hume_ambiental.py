from __future__ import annotations

from math import exp
from random import gauss

from app.enums.enums import TipoEvento
from app.models.sensor_simulado import SensorSimulado
from app.sensores.base import clamp, obtener_tipo_evento


def calcular_valor(datos_clima: dict, sensor: SensorSimulado, evento: dict | None, contexto: dict) -> tuple[float, str]:
	tipo_evento = obtener_tipo_evento(evento)
	if tipo_evento == TipoEvento.HELADA.value and sensor.ultimo_valor is not None:
		temperatura_base = sensor.ultimo_valor - 2.0
	else:
		temperatura_base = datos_clima["temperature_2m"] + gauss(0, 0.3)
	humedad_relativa = clamp(datos_clima["relative_humidity_2m"] + gauss(0, 2), 0, 100)
	psat = 0.6108 * exp((17.27 * temperatura_base) / (temperatura_base + 237.3))
	vpd = psat * (1 - humedad_relativa / 100)

	contexto["temperatura"] = temperatura_base
	contexto["humedad_relativa"] = humedad_relativa
	contexto["VPD"] = vpd

	return temperatura_base, "°C"