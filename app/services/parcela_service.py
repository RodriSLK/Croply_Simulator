from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.exceptions import ParcelaNoEncontradaError, ParcelaYaExisteError
from app.models.alerta_simulada import AlertaSimulada
from app.models.controlador_simulado import ControladorSimulado
from app.models.evento_manual_pendiente import EventoManualPendiente
from app.models.lectura_sensor_simulada import LecturaSensorSimulada
from app.models.parcela_simulada import ParcelaSimulada
from app.models.sensor_simulado import SensorSimulado
from app.schemas.parcela import ParcelaRequest


def _crear_controlador_y_sensores(db: Session, parcela_id: int, dto: ParcelaRequest) -> None:
	controlador = ControladorSimulado(
		controlador_id=dto.parcela.controlador.id,
		parcela_id=parcela_id,
		ip_controlador=dto.parcela.controlador.ip,
		estado=dto.parcela.controlador.estado,
	)
	db.add(controlador)

	for sensor in dto.parcela.controlador.sensores:
		db.add(
			SensorSimulado(
				sensor_id=sensor.id,
				controlador_id=dto.parcela.controlador.id,
				parcela_id=parcela_id,
				tipo=sensor.tipo,
			)
		)


def crear_parcela(db: Session, dto: ParcelaRequest) -> None:
	try:
		if db.get(ParcelaSimulada, dto.parcela.id) is not None:
			raise ParcelaYaExisteError(f"La parcela {dto.parcela.id} ya existe")

		db.add(
			ParcelaSimulada(
				parcela_id=dto.parcela.id,
				nombre=dto.parcela.nombre,
				latitud=dto.parcela.latitud,
				longitud=dto.parcela.longitud,
			)
		)
		db.flush()
		_crear_controlador_y_sensores(db, dto.parcela.id, dto)
		db.commit()
	except Exception:
		db.rollback()
		raise


def reemplazar_configuracion(db: Session, parcela_id: int, dto: ParcelaRequest) -> None:
	try:
		parcela = db.get(ParcelaSimulada, parcela_id)
		if parcela is None:
			raise ParcelaNoEncontradaError(f"La parcela {parcela_id} no existe")

		db.execute(delete(SensorSimulado).where(SensorSimulado.parcela_id == parcela_id))
		db.execute(delete(ControladorSimulado).where(ControladorSimulado.parcela_id == parcela_id))

		parcela.nombre = dto.parcela.nombre
		parcela.latitud = dto.parcela.latitud
		parcela.longitud = dto.parcela.longitud

		_crear_controlador_y_sensores(db, parcela_id, dto)
		db.commit()
	except Exception:
		db.rollback()
		raise


def eliminar_parcela(db: Session, parcela_id: int) -> None:
	try:
		parcela = db.get(ParcelaSimulada, parcela_id)
		if parcela is None:
			raise ParcelaNoEncontradaError(f"La parcela {parcela_id} no existe")

		db.delete(parcela)
		db.commit()
	except Exception:
		db.rollback()
		raise