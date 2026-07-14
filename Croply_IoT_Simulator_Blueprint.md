Croply IoT Simulator — Blueprint Técnico de Implementación

Tipo de proyecto: Práctica Profesional Supervisada (PPS) universitaria.
Estado: Especificación técnica oficial — lista para implementación.
Audiencia: Equipo de desarrollo, GitHub Copilot Pro.
Propósito: este documento es la especificación técnica oficial del simulador. Toda implementación debe respetar las decisiones aquí documentadas. Las decisiones arquitectónicas definidas no deben modificarse durante el desarrollo salvo que exista una justificación técnica de peso.


Filosofía del proyecto
Este proyecto prioriza los siguientes principios en todo momento:

Simplicidad. Evitar sobreingeniería. No implementar lo que no se necesita.
Bajo acoplamiento. Croply y el simulador son independientes. Se comunican solo por API REST.
Código mantenible. Claro, legible, organizado por responsabilidades.
Arquitectura clara. Estructura de carpetas predecible, nombres consistentes.
Fácil comprensión. Cualquier integrante del equipo debe poder entender el código sin contexto previo.
Fácil implementación. Stack acotado, sin dependencias innecesarias.

Ante dos soluciones técnicamente correctas, siempre elegir la más simple.

1. Descripción del sistema
El Croply IoT Simulator es un servicio web independiente escrito en Python que simula sensores agrícolas IoT. Se ejecuta localmente en desarrollo y demostraciones. No está pensado para producción ni alta concurrencia.
CROPLY (NestJS)
    ├── POST   /parcelas        →  registra nueva parcela
    ├── PUT    /parcelas/{id}   →  reemplaza configuración completa
    ├── DELETE /parcelas/{id}   →  elimina parcela y sus datos
    └── GET    /parcelas/{id}/estado  ←  estado actual (scheduler Croply)

SIMULADOR (FastAPI + Python)
    ├── Scheduler cada 25 min → Open-Meteo → calcula valores → persiste
    └── Panel HTML interno → visualización y eventos manuales
Principios de integración cerrados:

Croply nunca consulta el historial del simulador.
El simulador nunca escribe en Croply.
Cada sistema mantiene su propio historial.
La UI de Croply solo consulta su propia BD.
El simulador conserva exactamente los IDs recibidos de Croply.
Toda actualización usa PUT /parcelas/{id} con configuración completa. No hay endpoints individuales para controladores ni sensores.


2. Tecnologías y versiones
TecnologíaVersiónRolPython3.11+Lenguaje principalFastAPI0.111.xFramework web / API RESTUvicorn0.29.xServidor de desarrolloPydantic2.xValidación de DTOsSQLAlchemy2.xORM síncronoAlembic1.13.xMigraciones de BDpsycopg3.xDriver PostgreSQL síncronoPostgreSQL16.xBase de datosTimescaleDB2.xExtensión series temporalesAPScheduler3.10.xScheduler cada 25 minutoshttpx0.27.xCliente HTTP síncrono para Open-Meteopython-dotenv1.0.xVariables de entornoDocker25.xContenedorización localDocker Compose2.xOrquestación localpytest8.xTesting

3. Decisión: implementación síncrona
Decisión cerrada: el simulador usa un modelo de ejecución síncrono.
La programación async no aporta beneficios reales para este proyecto porque hay pocas parcelas (10-15), el scheduler corre cada 25 minutos, no hay usuarios concurrentes significativos, no hay WebSockets ni streaming. La complejidad que agrega async supera cualquier ganancia de rendimiento en este contexto.
Impacto:

database.py usa create_engine y Session síncronos.
Endpoints FastAPI con def, no async def.
httpx.Client síncrono (no AsyncClient).
APScheduler con BackgroundScheduler.
Tests con TestClient estándar, sin pytest-asyncio.


4. Estructura de carpetas
croply-iot-simulator/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── exceptions.py
│   ├── models/
│   │   ├── parcela_simulada.py
│   │   ├── controlador_simulado.py
│   │   ├── sensor_simulado.py
│   │   ├── lectura_sensor_simulada.py
│   │   ├── alerta_simulada.py
│   │   └── evento_manual_pendiente.py
│   ├── schemas/
│   │   ├── parcela.py
│   │   ├── sensor.py
│   │   ├── controlador.py
│   │   ├── lectura.py
│   │   ├── evento.py
│   │   └── status.py
│   ├── routers/
│   │   ├── parcelas.py
│   │   ├── estado.py
│   │   ├── lecturas.py
│   │   ├── eventos.py
│   │   ├── controlador.py
│   │   └── status.py
│   ├── services/
│   │   ├── parcela_service.py
│   │   ├── scheduler_service.py
│   │   ├── openmeteo_service.py
│   │   ├── evento_service.py
│   │   └── alerta_service.py
│   ├── sensores/
│   │   ├── base.py
│   │   ├── temp_hume_ambiental.py
│   │   ├── radiacion_solar.py
│   │   ├── precipitacion.py
│   │   ├── humedad_suelo.py
│   │   └── ph.py
│   ├── enums/
│   │   └── enums.py
│   └── static/
│       └── index.html
├── migrations/
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── test_parcelas.py
│   ├── test_estado.py
│   ├── test_scheduler.py
│   └── test_sensores/
│       ├── test_temp_hume.py
│       ├── test_radiacion.py
│       ├── test_precipitacion.py
│       ├── test_humedad_suelo.py
│       └── test_ph.py
├── .env
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
└── requirements.txt

5. Convenciones de nombres
Archivos: snake_case. Clases: PascalCase. Funciones/variables: snake_case. Constantes: UPPER_SNAKE_CASE.
Tablas de BD:
ClaseTablaParcelaSimuladaparcelas_simuladasControladorSimuladocontroladores_simuladosSensorSimuladosensores_simuladosLecturaSensorSimuladalecturas_simuladasAlertaSimuladaalertas_simuladasEventoManualPendienteeventos_manuales_pendientes
Enums definitivos — únicos valores válidos:
pythonclass TipoSensorEnum(str, Enum):
    TEMP_HUME_AMBIENTAL = "TEMP_HUME_AMBIENTAL"
    HUMEDAD_SUELO       = "HUMEDAD_SUELO"
    RADIACION_SOLAR     = "RADIACION_SOLAR"
    PRECIPITACION       = "PRECIPITACION"
    PH                  = "PH"

class EstadoTransmision(str, Enum):
    TRANSMITIENDO = "TRANSMITIENDO"
    SIN_SEÑAL     = "SIN_SEÑAL"

class TipoAlerta(str, Enum):
    HELADA = "HELADA"
    VWC_CRITICO = "VWC_CRITICO"
    SATURACION = "SATURACION"
    RIESGO_FUNGICO = "RIESGO_FUNGICO"
    ESTRES_HIDRICO = "ESTRES_HIDRICO"

class TipoEvento(str, Enum):
    RIEGO = "RIEGO"
    HELADA = "HELADA"
    LLUVIA = "LLUVIA"
    DERIVA_PH = "DERIVA_PH"
    DESCONECTAR_NODO = "DESCONECTAR_NODO"

6. Variables de entorno
envDATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/croply_simulator
SCHEDULER_INTERVAL_MINUTES=25
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1/forecast
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=development

7. Entidades del simulador
ParcelaSimulada
parcela_id (PK, int, de Croply), nombre, latitud, longitud, activa (bool, default True), creada_en (timestamp UTC).
ControladorSimulado
controlador_id (PK, int, de Croply), parcela_id (FK CASCADE), ip_controlador (nullable, no usado en cálculos), estado (EstadoTransmision, default TRANSMITIENDO).
SensorSimulado
sensor_id (PK, int, de Croply), controlador_id (FK CASCADE), parcela_id (FK CASCADE, desnormalizado), tipo (TipoSensorEnum), ip_sensor (nullable), ultimo_valor (float, nullable), fecha_ultima_lectura (timestamp, nullable), vwc_actual (float, nullable, solo HUMEDAD_SUELO), kc (float, nullable, default 0.4), profundidad_radicular (float, nullable, default 0.4), ph_base (float, nullable, default 6.5).
LecturaSensorSimulada
id (PK bigint autoincrement), sensor_id (FK CASCADE), parcela_id (FK CASCADE, desnormalizado), tipo_sensor (varchar, desnormalizado), valor (float), unidad (varchar), timestamp (timestamp UTC). TimescaleDB hypertable por timestamp.
AlertaSimulada
id (PK), parcela_id (FK CASCADE), tipo (TipoAlerta), valor_disparador (float), resuelta (bool, default False), timestamp.
EventoManualPendiente
id (PK), parcela_id (FK CASCADE), tipo_evento (TipoEvento), parametros (jsonb, default {}), aplicado (bool, default False), creado_en (timestamp UTC).

8. Índices
sqlCREATE INDEX idx_parcelas_activa ON parcelas_simuladas(activa);
CREATE INDEX idx_sensores_parcela ON sensores_simulados(parcela_id);
CREATE INDEX idx_eventos_pendientes ON eventos_manuales_pendientes(parcela_id, aplicado) WHERE aplicado = false;
CREATE INDEX idx_alertas_activas ON alertas_simuladas(parcela_id, resuelta) WHERE resuelta = false;

9. DTOs
POST /parcelas — entrada:
json{
  "parcela": {
    "id": 1, "nombre": "Parcela Norte", "latitud": -32.89, "longitud": -68.84,
    "controlador": {
      "id": 3, "ip": "192.168.0.10", "estado": "TRANSMITIENDO",
      "sensores": [
        {"id": 10, "tipo": "TEMP_HUME_AMBIENTAL"},
        {"id": 11, "tipo": "HUMEDAD_SUELO"},
        {"id": 12, "tipo": "RADIACION_SOLAR"},
        {"id": 13, "tipo": "PRECIPITACION"},
        {"id": 14, "tipo": "PH"}
      ]
    }
  }
}
PUT /parcelas/{id}: mismo schema que POST.
GET /parcelas/{id}/estado — salida:
json{
  "parcela_id": 1, "nombre": "Parcela Norte", "timestamp_simulacion": "...",
  "controladores": [{
    "controlador_id": 3,
    "sensores": [
      {"sensor_id": 10, "tipo": "TEMP_HUME_AMBIENTAL", "valor_actual": 23.4, "unidad": "°C", "fecha_ultima_lectura": "..."}
    ]
  }]
}
POST /parcelas/{id}/eventos — entrada:
json{"tipo": "RIEGO", "parametros": {"mm": 20}}
GET /status — salida:
json{"scheduler_activo": true, "ultima_ejecucion": "...", "proxima_ejecucion": "...", "parcelas_activas": 3}

10. Endpoints
MétodoPathLlamado porHTTP OKPOST/parcelasCroply201PUT/parcelas/{id}Croply200DELETE/parcelas/{id}Croply200GET/parcelas/{id}/estadoScheduler Croply200GET/parcelas/{id}/lecturasPanel interno200POST/parcelas/{id}/eventosPanel interno201PATCH/parcelas/{id}/controladorPanel interno200GET/statusPanel interno200
Errores: 404 (no encontrado), 409 (ya existe en POST), 422 (automático FastAPI), 500 (error interno, sin exponer traceback).

11. Scheduler
BackgroundScheduler de APScheduler. IntervalTrigger(minutes=25). Se inicia en el startup de FastAPI.
Ciclo por parcela (orden obligatorio):

Obtener parcelas con activa=True y controlador en TRANSMITIENDO.
Para cada parcela: cargar evento pendiente más antiguo (si hay).
Llamar a Open-Meteo. Si falla: log WARNING + skip parcela.
Inicializar contexto = {}.
Para cada sensor: llamar a calcular_valor(datos_clima, sensor, evento, contexto) → actualizar ultimo_valor + insertar LecturaSensorSimulada.
Evaluar alertas.
Marcar evento como aplicado = True.
Commit. Si falla: rollback de esta parcela + log ERROR + continuar con las demás.


12. Modelos de simulación
Todos los módulos implementan:
pythondef calcular_valor(datos_clima: dict, sensor: SensorSimulado, evento: dict | None, contexto: dict) -> tuple[float, str]:
TEMP_HUME_AMBIENTAL: T = temperature_2m + gauss(0, 0.3). HR = clamp(relative_humidity_2m + gauss(0, 2), 0, 100). VPD = Psat * (1 - HR/100). Guarda VPD en contexto. Retorna T en °C. Inserta lectura adicional de VPD en kPa. Evento HELADA: T = ultimo_valor - 2.0.
RADIACION_SOLAR: Rs = shortwave_radiation * (1 - cloud_cover/100 * 0.6) + gauss(0, Rs*0.05). ETo = 0.0135 * (T + 17.8) * sqrt(Rs * 0.0864). Guarda ETo en contexto. Retorna Rs en W/m².
PRECIPITACION: mm_intervalo = precipitation * 25/60. Pulsos = int(mm_intervalo / 0.2). mm_efectivos = pulsos * 0.2. lluvia_efectiva = max(0, mm_efectivos - 3). Guarda lluvia_efectiva en contexto. Retorna mm_efectivos. Evento LLUVIA: suma parametros["mm"].
HUMEDAD_SUELO (con estado): VWC inicial = 30.0 si vwc_actual es None. ETo_intervalo = ETo_diaria * 25/1440. VWC = vwc_actual - (ETo_intervalo * Kc)/(Pf*Z) + lluvia_efectiva/(Pf*Z*10). Clamp 0-100. Persiste vwc_actual. Retorna %. Evento RIEGO: suma parametros["mm"] a lluvia_efectiva.
PH: pH = ph_base + (-0.003 * dias) + (0.1 * sin(2π*hora/24)) + gauss(0, 0.02). Clamp 0-14. Retorna pH.

13. Open-Meteo
httpx.Client síncrono, timeout 10s. URL: https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,shortwave_radiation,precipitation,cloud_cover,wind_speed_10m&timezone=UTC. Sin API key. Una petición por parcela por ciclo. Si falla: lanza OpenMeteoError.

14. Eventos manuales
El scheduler carga el evento pendiente más antiguo antes de calcular sensores. Lo aplica como modificador en el sensor correspondiente. Lo marca aplicado = True después del commit. Efectos: RIEGO → suma mm a lluvia_efectiva en HUMEDAD_SUELO; HELADA → fuerza temperatura descendente; LLUVIA → suma mm a precipitación; DESCONECTAR_NODO → pone controlador en SIN_SEÑAL.

15. Alertas internas
TipoActivaciónResoluciónHELADAtemperatura < 2°Ctemperatura >= 2°CVWC_CRITICOvwc < 15%vwc >= 15%SATURACIONvwc > 60%vwc <= 60%RIESGO_FUNGICOHR > 80% y T entre 15-25°C en 2+ cicloscondición deja de cumplirseESTRES_HIDRICOVPD > 1.8 kPaVPD <= 1.8 kPa
No insertar duplicados. Resolver las activas cuando la condición cesa. Solo uso interno — Croply no las consulta.

16. Frontend del simulador
Un único index.html. Sin frameworks. Servido por FastAPI con StaticFiles. Muestra: barra de estado global (GET /status cada 60s), tabla por parcela con últimos valores (GET /estado al cargar), botones de eventos manuales, log en memoria JS, historial expandible (GET /lecturas?limit=50). Los datos de la tabla se actualizan manualmente ya que solo cambian cada 25 minutos.

17. Manejo de errores
Excepciones en app/exceptions.py: ParcelaNoEncontradaError, ParcelaYaExisteError, OpenMeteoError, SensorTipoDesconocidoError. Handler global en main.py para 500. Scheduler: nunca se detiene por error de una parcela individual.

18. Logs
Módulo estándar logging. Formato: %(asctime)s | %(levelname)-8s | %(name)s | %(message)s. Nivel leído de variable de entorno. Logger por módulo con logging.getLogger(__name__).

19. Persistencia
SQLAlchemy síncrono. create_engine con psycopg. Session con sessionmaker. get_db() como dependencia FastAPI. Scheduler crea sesiones directamente. Alembic gestiona migraciones. create_hypertable en la migración de lecturas_simuladas. Transacciones: POST/PUT atómicos; scheduler hace commit por parcela individualmente.
pythondef get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

20. Testing
Tests unitarios de sensores: sin BD, sin HTTP, entradas fijas, mocks simples. Tests de integración: TestClient de FastAPI, BD SQLite en memoria. Open-Meteo mockeado con unittest.mock. Ejecutar con pytest.

21. Docker
yamlservices:
  simulador:
    build: .
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/croply_simulator
      - SCHEDULER_INTERVAL_MINUTES=25
    depends_on:
      db:
        condition: service_healthy

  db:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: croply_simulator
    ports: ["5432:5432"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 5
Inicio: docker compose up -d db → docker compose run --rm simulador alembic upgrade head → docker compose up.

22. Orden de implementación
Fase 1 — Base: enums → config → database → models → Alembic + migraciones → verificar tablas en BD.
Fase 2 — API REST: exceptions → schemas → main.py → parcela_service → routers (parcelas, estado) → verificar con Swagger → tests de endpoints.
Fase 3 — Sensores: openmeteo_service → sensores/base → temp_hume → radiacion → precipitacion → humedad_suelo → ph → tests unitarios de sensores.
Fase 4 — Scheduler: evento_service → alerta_service → scheduler_service → registrar en startup → router status → router eventos → verificar ciclo manual → tests del scheduler.
Fase 5 — Frontend: index.html → StaticFiles → router lecturas → router controlador → verificar panel completo.
Fase 6 — Cierre: Dockerfile → docker-compose → verificar docker compose up → pytest completo.

23. Decisiones pendientes
DP-01 — Comportamiento del PUT con sensores nuevos
El PUT reemplaza toda la configuración. Si llegan sensores con IDs nuevos, se crean. Si faltan sensores que existían, se eliminan con su historial. Confirmar que este comportamiento es el esperado antes de implementar.
DP-02 — CORS
Para desarrollo local se puede abrir a todos los orígenes (*). Confirmar la URL de Croply local si hace falta restringirlo.
DP-03 — PUT sobre parcela con controlador en SIN_SEÑAL
El PUT reemplaza la configuración incluyendo el estado del controlador. Si el DTO envía TRANSMITIENDO, el controlador se reactiva. Confirmar con el equipo.
DP-04 — Zona horaria en respuestas JSON
Se asume UTC en todas las respuestas. Confirmar con el equipo de Croply si esperan zona horaria local.

Blueprint técnico oficial — Croply IoT Simulator — Julio 2026.