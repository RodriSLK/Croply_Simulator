from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.parcela import ParcelaRequest
from app.services.parcela_service import crear_parcela, eliminar_parcela, reemplazar_configuracion


router = APIRouter()


@router.post("/parcelas", status_code=status.HTTP_201_CREATED)
def crear_parcela_endpoint(dto: ParcelaRequest, db: Session = Depends(get_db)) -> dict[str, str]:
	crear_parcela(db, dto)
	return {"detail": "Parcela creada"}


@router.put("/parcelas/{parcela_id}")
def reemplazar_parcela_endpoint(parcela_id: int, dto: ParcelaRequest, db: Session = Depends(get_db)) -> dict[str, str]:
	reemplazar_configuracion(db, parcela_id, dto)
	return {"detail": "Parcela actualizada"}


@router.delete("/parcelas/{parcela_id}")
def eliminar_parcela_endpoint(parcela_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
	eliminar_parcela(db, parcela_id)
	return {"detail": "Parcela eliminada"}