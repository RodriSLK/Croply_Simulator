from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.config import setup_logging
from app.exceptions import ParcelaNoEncontradaError, ParcelaYaExisteError
from app.routers.controlador import router as controlador_router
from app.routers.estado import router as estado_router
from app.routers.eventos import router as eventos_router
from app.routers.lecturas import router as lecturas_router
from app.routers.parcelas import router as parcelas_router
from app.routers.status import router as status_router
from app.services.scheduler_service import detener_scheduler, iniciar_scheduler

setup_logging()

app = FastAPI()
app.include_router(parcelas_router)
app.include_router(estado_router)
app.include_router(lecturas_router)
app.include_router(eventos_router)
app.include_router(controlador_router)
app.include_router(status_router)


@app.on_event("startup")
def start_scheduler() -> None:
    iniciar_scheduler()


@app.on_event("shutdown")
def stop_scheduler() -> None:
    detener_scheduler()


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