from __future__ import annotations

from fastapi import APIRouter

from app.schemas.status import StatusResponse
from app.services.scheduler_service import obtener_estado_scheduler


router = APIRouter()


@router.get("/status", response_model=StatusResponse)
def obtener_status() -> StatusResponse:
	return StatusResponse.model_validate(obtener_estado_scheduler())