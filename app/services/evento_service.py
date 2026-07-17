from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.evento_manual_pendiente import EventoManualPendiente
from app.schemas.evento import EventoEntrada


def obtener_evento_pendiente_mas_antiguo(db: Session, parcela_id: int) -> EventoManualPendiente | None:
	stmt = (
		select(EventoManualPendiente)
		.where(
			EventoManualPendiente.parcela_id == parcela_id,
			EventoManualPendiente.aplicado.is_(False),
		)
		.order_by(EventoManualPendiente.creado_en.asc(), EventoManualPendiente.id.asc())
	)
	return db.scalars(stmt).first()


def crear_evento_pendiente(db: Session, parcela_id: int, dto: EventoEntrada) -> EventoManualPendiente:
	evento = EventoManualPendiente(
		parcela_id=parcela_id,
		tipo_evento=dto.tipo,
		parametros=dict(dto.parametros),
	)

	try:
		db.add(evento)
		db.commit()
		db.refresh(evento)
		return evento
	except Exception:
		db.rollback()
		raise


def marcar_evento_aplicado(
	db: Session,
	evento: EventoManualPendiente,
	*,
	commit: bool = True,
) -> EventoManualPendiente:
	evento.aplicado = True

	if commit:
		try:
			db.commit()
			db.refresh(evento)
		except Exception:
			db.rollback()
			raise

	return evento