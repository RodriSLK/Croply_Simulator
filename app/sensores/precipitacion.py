from __future__ import annotations

from random import gauss

from app.enums.enums import TipoEvento
from app.models.sensor_simulado import SensorSimulado
from app.sensores.base import clamp, obtener_parametros_evento, obtener_tipo_evento


def calcular_valor(datos_clima: dict, sensor: SensorSimulado, evento: dict | None, contexto: dict) -> tuple[float, str]:
	lluvia_evento = 0.0
	if obtener_tipo_evento(evento) == TipoEvento.LLUVIA.value:
		lluvia_evento = float(obtener_parametros_evento(evento).get("mm", 0))

	precipitacion_total = datos_clima["precipitation"] + lluvia_evento
	mm_intervalo = precipitacion_total * 25 / 60
	pulsos = int(mm_intervalo / 0.2)
	mm_efectivos = pulsos * 0.2
	lluvia_efectiva = max(0.0, mm_efectivos - 3)

	contexto["lluvia_efectiva"] = lluvia_efectiva

	return mm_efectivos, "mm"