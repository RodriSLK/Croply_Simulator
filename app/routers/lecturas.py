from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.lectura_sensor_simulada import LecturaSensorSimulada
from app.schemas.lectura import LecturasResponse


router = APIRouter()


@router.get("/parcelas/{parcela_id}/lecturas", response_model=LecturasResponse)
def obtener_lecturas_parcela(
	parcela_id: int,
	limit: int = 50,
	db: Session = Depends(get_db),
) -> LecturasResponse:
	lecturas = list(
		db.scalars(
			select(LecturaSensorSimulada)
			.where(LecturaSensorSimulada.parcela_id == parcela_id)
			.order_by(LecturaSensorSimulada.timestamp.desc(), LecturaSensorSimulada.id.desc())
			.limit(limit)
		).all()
	)
	return LecturasResponse(lecturas=lecturas)