from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

load_dotenv()

class Settings:
	DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://usuario:password@localhost:5432/croply_simulator")
	SCHEDULER_INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "25"))
	OPEN_METEO_BASE_URL = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1/forecast")
	APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
	APP_PORT = int(os.getenv("APP_PORT", "8000"))
	LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
	ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

settings = Settings()

def setup_logging(level: str | None = None) -> None:
	logging.basicConfig(
		level=getattr(logging, (level or settings.LOG_LEVEL).upper(), logging.INFO),
		format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
	)
# Configuracion de entorno y variables del simulador.