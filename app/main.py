from fastapi import FastAPI
from app.config import setup_logging

setup_logging()

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}