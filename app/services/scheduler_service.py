from __future__ import annotations

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.enums.enums import EstadoTransmision, TipoEvento, TipoSensorEnum
from app.models.alerta_simulada import AlertaSimulada
from app.models.controlador_simulado import ControladorSimulado
from app.models.evento_manual_pendiente import EventoManualPendiente
from app.models.lectura_sensor_simulada import LecturaSensorSimulada
from app.models.parcela_simulada import ParcelaSimulada
from app.models.sensor_simulado import SensorSimulado
from app.services.alerta_service import evaluar_alertas_parcela
from app.services.evento_service import marcar_evento_aplicado, obtener_evento_pendiente_mas_antiguo
from app.services.openmeteo_service import obtener_clima_actual
from app.sensores import humedad_suelo, ph, precipitacion, radiacion_solar, temp_hume_ambiental

logger = logging.getLogger(__name__)

JOB_ID = "ciclo_simulacion"

_scheduler: BackgroundScheduler | None = None
_ultima_ejecucion: datetime | None = None


_ORDEN_SENSORES = {
	TipoSensorEnum.TEMP_HUME_AMBIENTAL: 0,
	TipoSensorEnum.RADIACION_SOLAR: 1,
	TipoSensorEnum.PRECIPITACION: 2,
	TipoSensorEnum.HUMEDAD_SUELO: 3,
	TipoSensorEnum.PH: 4,
}


_CICLO_SENSORES = {
	TipoSensorEnum.TEMP_HUME_AMBIENTAL: temp_hume_ambiental.calcular_valor,
	TipoSensorEnum.RADIACION_SOLAR: radiacion_solar.calcular_valor,
	TipoSensorEnum.PRECIPITACION: precipitacion.calcular_valor,
	TipoSensorEnum.HUMEDAD_SUELO: humedad_suelo.calcular_valor,
	TipoSensorEnum.PH: ph.calcular_valor,
}


def _obtener_scheduler() -> BackgroundScheduler:
	global _scheduler
	if _scheduler is None:
		_scheduler = BackgroundScheduler()
	return _scheduler


def scheduler_activo() -> bool:
	scheduler = _scheduler
	return scheduler is not None and scheduler.running


def iniciar_scheduler() -> None:
	scheduler = _obtener_scheduler()
	if scheduler.get_job(JOB_ID) is None:
		scheduler.add_job(
			ejecutar_ciclo_simulacion,
			IntervalTrigger(minutes=settings.SCHEDULER_INTERVAL_MINUTES),
			id=JOB_ID,
			replace_existing=True,
			max_instances=1,
			coalesce=True,
		)
	if not scheduler.running:
		scheduler.start()
		logger.info("Scheduler iniciado")


def detener_scheduler() -> None:
	global _scheduler
	scheduler = _scheduler
	if scheduler is not None and scheduler.running:
		scheduler.shutdown(wait=False)
		logger.info("Scheduler detenido")
	_scheduler = None


def obtener_estado_scheduler() -> dict[str, object]:
	scheduler = _scheduler
	next_run_time = None
	if scheduler is not None and scheduler.running:
		job = scheduler.get_job(JOB_ID)
		if job is not None and job.next_run_time is not None:
			next_run_time = job.next_run_time

	with SessionLocal() as db:
		parcelas_activas = db.scalar(select(func.count()).select_from(ParcelaSimulada).where(ParcelaSimulada.activa.is_(True)))

	return {
		"scheduler_activo": scheduler_activo(),
		"ultima_ejecucion": _ultima_ejecucion,
		"proxima_ejecucion": next_run_time,
		"parcelas_activas": parcelas_activas or 0,
	}


def _obtener_sensores_ordenados(db: Session, parcela_id: int) -> list[SensorSimulado]:
	sensores = list(
		db.scalars(
			select(SensorSimulado).where(SensorSimulado.parcela_id == parcela_id)
		).all()
	)
	return sorted(sensores, key=lambda sensor: _ORDEN_SENSORES[sensor.tipo])


def _obtener_evento_como_dict(evento: EventoManualPendiente | None) -> dict[str, object] | None:
	if evento is None:
		return None
	return {
		"tipo": evento.tipo_evento,
		"parametros": dict(evento.parametros or {}),
	}


def _procesar_parcela(db: Session, parcela: ParcelaSimulada) -> None:
	controlador = db.scalar(
		select(ControladorSimulado).where(ControladorSimulado.parcela_id == parcela.parcela_id)
	)
	if controlador is None or controlador.estado != EstadoTransmision.TRANSMITIENDO:
		return

	evento = obtener_evento_pendiente_mas_antiguo(db, parcela.parcela_id)

	if evento is not None and evento.tipo_evento == TipoEvento.DESCONECTAR_NODO:
		controlador.estado = EstadoTransmision.SIN_SEÑAL
		marcar_evento_aplicado(db, evento, commit=False)
		db.commit()
		return

	try:
		datos_clima = obtener_clima_actual(parcela.latitud, parcela.longitud)
	except Exception as exc:
		logger.warning("Open-Meteo falló para parcela %s: %s", parcela.parcela_id, exc)
		db.rollback()
		return

	contexto: dict[str, float] = {}
	evento_dict = _obtener_evento_como_dict(evento)
	hora_ahora = datetime.now(timezone.utc)

	for sensor in _obtener_sensores_ordenados(db, parcela.parcela_id):
		calcular_valor = _CICLO_SENSORES.get(sensor.tipo)
		if calcular_valor is None:
			raise ValueError(f"Tipo de sensor no soportado: {sensor.tipo}")

		valor, unidad = calcular_valor(datos_clima, sensor, evento_dict, contexto)
		sensor.ultimo_valor = valor
		sensor.fecha_ultima_lectura = hora_ahora
		db.add(
			LecturaSensorSimulada(
				sensor_id=sensor.sensor_id,
				parcela_id=parcela.parcela_id,
				tipo_sensor=sensor.tipo.value,
				valor=valor,
				unidad=unidad,
				timestamp=hora_ahora,
			)
		)

	if "temperatura" in contexto and "humedad_relativa" in contexto and "vwc" in contexto and "VPD" in contexto:
		evaluar_alertas_parcela(
			db,
			parcela.parcela_id,
			temperatura=float(contexto["temperatura"]),
			humedad_relativa=float(contexto["humedad_relativa"]),
			vwc=float(contexto["vwc"]),
			vpd=float(contexto["VPD"]),
		)

	if evento is not None:
		marcar_evento_aplicado(db, evento, commit=False)

	db.commit()


def ejecutar_ciclo_simulacion(session_factory: type[Session] | None = None) -> None:
	global _ultima_ejecucion
	factory = session_factory or SessionLocal
	with factory() as db:
		parcelas = list(
			db.scalars(
				select(ParcelaSimulada)
				.join(ControladorSimulado, ControladorSimulado.parcela_id == ParcelaSimulada.parcela_id)
				.where(
					ParcelaSimulada.activa.is_(True),
					ControladorSimulado.estado == EstadoTransmision.TRANSMITIENDO,
				)
			)
			.all()
		)

		for parcela in parcelas:
			try:
				_procesar_parcela(db, parcela)
			except Exception as exc:
				logger.error("Error procesando parcela %s: %s", parcela.parcela_id, exc)
				db.rollback()
				continue

	_ultima_ejecucion = datetime.now(timezone.utc)