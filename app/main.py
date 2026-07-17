from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.config import setup_logging
from app.exceptions import ParcelaNoEncontradaError, ParcelaYaExisteError
from app.routers.estado import router as estado_router
from app.routers.parcelas import router as parcelas_router

setup_logging()

app = FastAPI()
app.include_router(parcelas_router)
app.include_router(estado_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(ParcelaNoEncontradaError)
def handle_parcela_no_encontrada(_: Request, exc: ParcelaNoEncontradaError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc) or "Parcela no encontrada"})


@app.exception_handler(ParcelaYaExisteError)
def handle_parcela_ya_existe(_: Request, exc: ParcelaYaExisteError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc) or "Parcela ya existe"})


@app.exception_handler(Exception)
def handle_unexpected_error(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal Server Error"})