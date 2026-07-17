from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class StatusResponse(BaseModel):
	scheduler_activo: bool
	ultima_ejecucion: datetime | None = None
	proxima_ejecucion: datetime | None = None
	parcelas_activas: int