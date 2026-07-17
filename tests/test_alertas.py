from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.enums.enums import TipoAlerta
from app.models.alerta_simulada import AlertaSimulada
from app.models.parcela_simulada import ParcelaSimulada
from app.services.alerta_service import evaluar_alertas_parcela, reiniciar_estado_alertas


ENGINE = create_engine("postgresql+psycopg://usuario:password@localhost:5432/croply_simulator")
SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)


def _limpiar_tablas() -> None:
	with ENGINE.begin() as connection:
		connection.execute(text("TRUNCATE TABLE alertas_simuladas, parcelas_simuladas RESTART IDENTITY CASCADE"))
	reiniciar_estado_alertas()


def _contar_alertas(db, parcela_id: int, tipo: TipoAlerta | None = None) -> int:
	query = db.query(AlertaSimulada).filter(AlertaSimulada.parcela_id == parcela_id)
	if tipo is not None:
		query = query.filter(AlertaSimulada.tipo == tipo)
	return query.count()


def _crear_parcela(db, parcela_id: int) -> None:
	db.add(
		ParcelaSimulada(
			parcela_id=parcela_id,
			nombre=f"Parcela {parcela_id}",
			latitud=-32.89,
			longitud=-68.84,
		)
	)
	db.commit()


def test_helada_activa_y_no_duplica() -> None:
	_limpiar_tablas()
	db = SessionLocal()
	try:
		_crear_parcela(db, 1)
		resultado = evaluar_alertas_parcela(db, 1, temperatura=1.5, humedad_relativa=50, vwc=30, vpd=1.0)
		assert resultado[TipoAlerta.HELADA] is not None
		assert _contar_alertas(db, 1, TipoAlerta.HELADA) == 1

		resultado = evaluar_alertas_parcela(db, 1, temperatura=1.0, humedad_relativa=50, vwc=30, vpd=1.0)
		assert resultado[TipoAlerta.HELADA] is not None
		assert _contar_alertas(db, 1, TipoAlerta.HELADA) == 1

		resultado = evaluar_alertas_parcela(db, 1, temperatura=2.0, humedad_relativa=50, vwc=30, vpd=1.0)
		assert resultado[TipoAlerta.HELADA] is not None
		assert resultado[TipoAlerta.HELADA].resuelta is True
	finally:
		db.close()


def test_vwc_critico_activa_y_resuelve() -> None:
	_limpiar_tablas()
	db = SessionLocal()
	try:
		_crear_parcela(db, 2)
		resultado = evaluar_alertas_parcela(db, 2, temperatura=20, humedad_relativa=50, vwc=14.9, vpd=1.0)
		assert resultado[TipoAlerta.VWC_CRITICO] is not None
		assert resultado[TipoAlerta.VWC_CRITICO].resuelta is False

		resultado = evaluar_alertas_parcela(db, 2, temperatura=20, humedad_relativa=50, vwc=15.0, vpd=1.0)
		assert resultado[TipoAlerta.VWC_CRITICO] is not None
		assert resultado[TipoAlerta.VWC_CRITICO].resuelta is True
	finally:
		db.close()


def test_saturacion_activa_y_resuelve() -> None:
	_limpiar_tablas()
	db = SessionLocal()
	try:
		_crear_parcela(db, 3)
		resultado = evaluar_alertas_parcela(db, 3, temperatura=20, humedad_relativa=50, vwc=60.1, vpd=1.0)
		assert resultado[TipoAlerta.SATURACION] is not None
		assert resultado[TipoAlerta.SATURACION].resuelta is False

		resultado = evaluar_alertas_parcela(db, 3, temperatura=20, humedad_relativa=50, vwc=60.0, vpd=1.0)
		assert resultado[TipoAlerta.SATURACION] is not None
		assert resultado[TipoAlerta.SATURACION].resuelta is True
	finally:
		db.close()


def test_estres_hidrico_activa_y_resuelve() -> None:
	_limpiar_tablas()
	db = SessionLocal()
	try:
		_crear_parcela(db, 4)
		resultado = evaluar_alertas_parcela(db, 4, temperatura=20, humedad_relativa=50, vwc=30, vpd=1.81)
		assert resultado[TipoAlerta.ESTRES_HIDRICO] is not None
		assert resultado[TipoAlerta.ESTRES_HIDRICO].resuelta is False

		resultado = evaluar_alertas_parcela(db, 4, temperatura=20, humedad_relativa=50, vwc=30, vpd=1.8)
		assert resultado[TipoAlerta.ESTRES_HIDRICO] is not None
		assert resultado[TipoAlerta.ESTRES_HIDRICO].resuelta is True
	finally:
		db.close()


def test_riesgo_fungico_requiere_dos_ciclos_y_resuelve() -> None:
	_limpiar_tablas()
	db = SessionLocal()
	try:
		_crear_parcela(db, 5)
		resultado = evaluar_alertas_parcela(db, 5, temperatura=20, humedad_relativa=85, vwc=30, vpd=1.0)
		assert resultado[TipoAlerta.RIESGO_FUNGICO] is None
		assert _contar_alertas(db, 5, TipoAlerta.RIESGO_FUNGICO) == 0

		resultado = evaluar_alertas_parcela(db, 5, temperatura=20, humedad_relativa=85, vwc=30, vpd=1.0)
		assert resultado[TipoAlerta.RIESGO_FUNGICO] is not None
		assert resultado[TipoAlerta.RIESGO_FUNGICO].resuelta is False
		assert _contar_alertas(db, 5, TipoAlerta.RIESGO_FUNGICO) == 1

		resultado = evaluar_alertas_parcela(db, 5, temperatura=20, humedad_relativa=85, vwc=30, vpd=1.0)
		assert resultado[TipoAlerta.RIESGO_FUNGICO] is not None
		assert _contar_alertas(db, 5, TipoAlerta.RIESGO_FUNGICO) == 1

		resultado = evaluar_alertas_parcela(db, 5, temperatura=10, humedad_relativa=50, vwc=30, vpd=1.0)
		assert resultado[TipoAlerta.RIESGO_FUNGICO] is not None
		assert resultado[TipoAlerta.RIESGO_FUNGICO].resuelta is True
	finally:
		db.close()