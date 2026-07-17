from __future__ import annotations

from math import sqrt
from random import gauss

from app.models.sensor_simulado import SensorSimulado
from app.sensores.base import clamp


def calcular_valor(datos_clima: dict, sensor: SensorSimulado, evento: dict | None, contexto: dict) -> tuple[float, str]:
	radiacion_base = datos_clima["shortwave_radiation"] * (1 - (datos_clima["cloud_cover"] / 100) * 0.6)
	radiacion = radiacion_base + gauss(0, radiacion_base * 0.05)
	temperatura = contexto.get("temperatura", datos_clima["temperature_2m"])
	eto = 0.0135 * (temperatura + 17.8) * sqrt(max(radiacion, 0) * 0.0864)

	contexto["ETo"] = eto

	return radiacion, "W/m²"