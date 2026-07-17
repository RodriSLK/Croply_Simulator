from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.enums.enums import TipoEvento


class EventoEntrada(BaseModel):
	tipo: TipoEvento
	parametros: dict[str, Any] = Field(default_factory=dict)