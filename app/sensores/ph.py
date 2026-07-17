from __future__ import annotations

from datetime import datetime, timezone
from math import pi, sin
from random import gauss

from app.models.sensor_simulado import SensorSimulado
from app.sensores.base import clamp


def calcular_valor(datos_clima: dict, sensor: SensorSimulado, evento: dict | None, contexto: dict) -> tuple[float, str]:
	ahora = datetime.now(timezone.utc)
	if sensor.fecha_ultima_lectura is None:
		dias = 0.0
	else:
		diferencia = ahora - sensor.fecha_ultima_lectura
		dias = diferencia.total_seconds() / 86400

	hora_decimal = ahora.hour + ahora.minute / 60 + ahora.second / 3600
	ph = (sensor.ph_base or 6.5) + (-0.003 * dias) + (0.1 * sin((2 * pi * hora_decimal) / 24)) + gauss(0, 0.02)
	ph = clamp(ph, 0, 14)

	return ph, "pH"