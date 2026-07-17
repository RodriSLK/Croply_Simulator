from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.evento import EventoEntrada
from app.services.evento_service import crear_evento_pendiente


router = APIRouter()


@router.post("/parcelas/{parcela_id}/eventos", status_code=status.HTTP_201_CREATED)
def crear_evento_endpoint(
	parcela_id: int,
	dto: EventoEntrada,
	db: Session = Depends(get_db),
) -> dict[str, str]:
	crear_evento_pendiente(db, parcela_id, dto)
	return {"detail": "Evento creado"}