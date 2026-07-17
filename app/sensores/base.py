from __future__ import annotations

from typing import Any


def clamp(valor: float, minimo: float, maximo: float) -> float:
	return max(minimo, min(maximo, valor))


def obtener_tipo_evento(evento: Any) -> str | None:
	if evento is None:
		return None
	if hasattr(evento, "value"):
		return str(evento.value)
	if isinstance(evento, dict):
		tipo = evento.get("tipo") or evento.get("tipo_evento")
		if hasattr(tipo, "value"):
			return str(tipo.value)
		return str(tipo) if tipo is not None else None
	return str(evento)


def obtener_parametros_evento(evento: Any) -> dict[str, Any]:
	if evento is None:
		return {}
	if isinstance(evento, dict):
		parametros = evento.get("parametros") or {}
		return dict(parametros)
	return {}
