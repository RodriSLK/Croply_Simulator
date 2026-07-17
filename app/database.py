from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[object, None, None]:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
# Configuracion de persistencia SQLAlchemy del simulador.