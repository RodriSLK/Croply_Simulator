from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums.enums import TipoAlerta
from app.models.alerta_simulada import AlertaSimulada


_riesgo_fungico_ciclos: dict[int, int] = defaultdict(int)


def reiniciar_estado_alertas() -> None:
	_riesgo_fungico_ciclos.clear()


def _obtener_alerta_activa(db: Session, parcela_id: int, tipo: TipoAlerta) -> AlertaSimulada | None:
	stmt = select(AlertaSimulada).where(
		AlertaSimulada.parcela_id == parcela_id,
		AlertaSimulada.tipo == tipo,
		AlertaSimulada.resuelta.is_(False),
	)
	return db.scalars(stmt).first()


def _crear_alerta(db: Session, parcela_id: int, tipo: TipoAlerta, valor_disparador: float) -> AlertaSimulada:
	alerta = AlertaSimulada(
		parcela_id=parcela_id,
		tipo=tipo,
		valor_disparador=valor_disparador,
		resuelta=False,
	)
	db.add(alerta)
	db.flush()
	return alerta


def _resolver_alerta(db: Session, alerta: AlertaSimulada) -> AlertaSimulada:
	alerta.resuelta = True
	db.flush()
	return alerta


def _evaluar_regla_simple(
	db: Session,
	parcela_id: int,
	tipo: TipoAlerta,
	condicion_activa: bool,
	valor_disparador: float,
) -> AlertaSimulada | None:
	alerta_activa = _obtener_alerta_activa(db, parcela_id, tipo)

	if condicion_activa:
		if alerta_activa is None:
			return _crear_alerta(db, parcela_id, tipo, valor_disparador)
		return alerta_activa

	if alerta_activa is not None:
		return _resolver_alerta(db, alerta_activa)

	return None


def evaluar_alertas_parcela(
	db: Session,
	parcela_id: int,
	*,
	temperatura: float,
	humedad_relativa: float,
	vwc: float,
	vpd: float,
) -> dict[TipoAlerta, AlertaSimulada | None]:
	resultados: dict[TipoAlerta, AlertaSimulada | None] = {}

	resultados[TipoAlerta.HELADA] = _evaluar_regla_simple(
		db,
		parcela_id,
		TipoAlerta.HELADA,
		temperatura < 2,
		temperatura,
	)
	resultados[TipoAlerta.VWC_CRITICO] = _evaluar_regla_simple(
		db,
		parcela_id,
		TipoAlerta.VWC_CRITICO,
		vwc < 15,
		vwc,
	)
	resultados[TipoAlerta.SATURACION] = _evaluar_regla_simple(
		db,
		parcela_id,
		TipoAlerta.SATURACION,
		vwc > 60,
		vwc,
	)
	resultados[TipoAlerta.ESTRES_HIDRICO] = _evaluar_regla_simple(
		db,
		parcela_id,
		TipoAlerta.ESTRES_HIDRICO,
		vpd > 1.8,
		vpd,
	)

	alerta_fungica = _obtener_alerta_activa(db, parcela_id, TipoAlerta.RIESGO_FUNGICO)
	condicion_fungica = humedad_relativa > 80 and 15 <= temperatura <= 25

	if condicion_fungica:
		_riesgo_fungico_ciclos[parcela_id] += 1
		if alerta_fungica is None and _riesgo_fungico_ciclos[parcela_id] >= 2:
			resultados[TipoAlerta.RIESGO_FUNGICO] = _crear_alerta(db, parcela_id, TipoAlerta.RIESGO_FUNGICO, humedad_relativa)
		else:
			resultados[TipoAlerta.RIESGO_FUNGICO] = alerta_fungica
	else:
		_riesgo_fungico_ciclos[parcela_id] = 0
		if alerta_fungica is not None:
			resultados[TipoAlerta.RIESGO_FUNGICO] = _resolver_alerta(db, alerta_fungica)
		else:
			resultados[TipoAlerta.RIESGO_FUNGICO] = None

	return resultados