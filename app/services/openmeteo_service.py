from __future__ import annotations

from typing import Any

import httpx

from app.config import settings
from app.exceptions import OpenMeteoError


def obtener_clima_actual(latitud: float, longitud: float) -> dict[str, float]:
    url = (
        f"{settings.OPEN_METEO_BASE_URL}?latitude={latitud}&longitude={longitud}"
        "&current=temperature_2m,relative_humidity_2m,shortwave_radiation,precipitation,cloud_cover,wind_speed_10m"
        "&timezone=UTC"
    )

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        raise OpenMeteoError("No se pudo obtener datos climáticos") from exc

    current = payload.get("current")
    if not isinstance(current, dict):
        raise OpenMeteoError("Respuesta de Open-Meteo inválida")

    required_fields = [
        "temperature_2m",
        "relative_humidity_2m",
        "shortwave_radiation",
        "precipitation",
        "cloud_cover",
        "wind_speed_10m",
    ]

    try:
        return {field: float(current[field]) for field in required_fields}
    except (KeyError, TypeError, ValueError) as exc:
        raise OpenMeteoError("Respuesta de Open-Meteo incompleta") from exc
