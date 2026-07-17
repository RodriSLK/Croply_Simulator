from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums.enums import EstadoTransmision
from app.exceptions import ParcelaNoEncontradaError
from app.models.controlador_simulado import ControladorSimulado
from app.schemas.controlador import ControladorPatchRequest


router = APIRouter()


@router.patch("/parcelas/{parcela_id}/controlador")
def actualizar_controlador(
	parcela_id: int,
	dto: ControladorPatchRequest,
	db: Session = Depends(get_db),
) -> dict[str, str]:
	controlador = db.scalar(select(ControladorSimulado).where(ControladorSimulado.parcela_id == parcela_id))
	if controlador is None:
		raise ParcelaNoEncontradaError(f"La parcela {parcela_id} no existe")

	controlador.estado = dto.estado
	db.commit()
	return {"detail": "Controlador actualizado"}