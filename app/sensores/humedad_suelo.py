from __future__ import annotations

from app.enums.enums import TipoEvento
from app.models.sensor_simulado import SensorSimulado
from app.sensores.base import clamp, obtener_parametros_evento, obtener_tipo_evento


def calcular_valor(datos_clima: dict, sensor: SensorSimulado, evento: dict | None, contexto: dict) -> tuple[float, str]:
	lluvia_efectiva = float(contexto.get("lluvia_efectiva", 0.0))
	if obtener_tipo_evento(evento) == TipoEvento.RIEGO.value:
		lluvia_efectiva += float(obtener_parametros_evento(evento).get("mm", 0))

	eto_diaria = float(contexto.get("ETo", 0.0))
	eto_intervalo = eto_diaria * 25 / 1440
	vwc_base = sensor.vwc_actual if sensor.vwc_actual is not None else 30.0
	kc = sensor.kc or 0.4
	profundidad = sensor.profundidad_radicular or 0.4
	pf = 1.0

	vwc = vwc_base - (eto_intervalo * kc) / (pf * profundidad) + lluvia_efectiva / (pf * profundidad * 10)
	vwc = clamp(vwc, 0, 100)
	sensor.vwc_actual = vwc

	contexto["vwc"] = vwc

	return vwc, "%"