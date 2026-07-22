from __future__ import annotations

from datetime import datetime, timezone, timedelta

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.evento_manual_pendiente import EventoManualPendiente
from app.schemas.evento import EventoEntrada
from app.services.evento_service import (
	crear_evento_pendiente,
	marcar_evento_aplicado,
	obtener_evento_pendiente_mas_antiguo,
)


ENGINE = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)


def _limpiar_tablas() -> None:
	with ENGINE.begin() as connection:
		connection.execute(text("TRUNCATE TABLE eventos_manuales_pendientes RESTART IDENTITY CASCADE"))


def _dto_evento() -> EventoEntrada:
	return EventoEntrada.model_validate({"tipo": "RIEGO", "parametros": {"mm": 20}})


def test_crear_evento_pendiente_persiste_registro() -> None:
	_limpiar_tablas()
	db = SessionLocal()
	try:
		evento = crear_evento_pendiente(db, 1, _dto_evento())

		assert evento.id is not None
		assert evento.parcela_id == 1
		assert evento.aplicado is False
		assert evento.tipo_evento.value == "RIEGO"
		assert db.get(EventoManualPendiente, evento.id) is not None
	finally:
		db.close()


def test_obtener_evento_pendiente_mas_antiguo_respeta_orden() -> None:
	_limpiar_tablas()
	db = SessionLocal()
	try:
		primero = EventoManualPendiente(
			parcela_id=1,
			tipo_evento="RIEGO",
			parametros={"mm": 10},
			aplicado=False,
			creado_en=datetime.now(timezone.utc) - timedelta(minutes=10),
		)
		segundo = EventoManualPendiente(
			parcela_id=1,
			tipo_evento="LLUVIA",
			parametros={"mm": 5},
			aplicado=False,
			creado_en=datetime.now(timezone.utc) - timedelta(minutes=1),
		)
		db.add_all([primero, segundo])
		db.commit()

		evento = obtener_evento_pendiente_mas_antiguo(db, 1)

		assert evento is not None
		assert evento.id == primero.id
		assert evento.tipo_evento.value == "RIEGO"
	finally:
		db.close()


def test_marcar_evento_aplicado_lo_saca_de_pendientes() -> None:
	_limpiar_tablas()
	db = SessionLocal()
	try:
		evento = crear_evento_pendiente(db, 1, _dto_evento())

		marcar_evento_aplicado(db, evento)

		assert db.get(EventoManualPendiente, evento.id).aplicado is True
		assert obtener_evento_pendiente_mas_antiguo(db, 1) is None
	finally:
		db.close()