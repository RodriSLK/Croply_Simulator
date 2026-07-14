# Croply IoT Simulator — Plan de Implementación

> **Tipo de documento:** Plan de implementación paso a paso, para ejecución por GitHub Copilot Pro.
> **No contiene:** arquitectura, teoría, justificaciones, diagramas ni casos de uso. Toda esa información ya está cerrada en `Croply_IoT_Simulator_Documentacion_Tecnica.md` (Documentación Funcional) y en `Croply_IoT_Simulator_Blueprint.md` (Blueprint Técnico). Este documento asume que ambos ya están disponibles como contexto y **remite a sus secciones** en lugar de repetirlas.
> **Regla de oro:** no avanzar a la fase siguiente hasta que la fase actual cumpla su **Criterio de finalización**. Ninguna fase debe implementar nada que pertenezca a una fase posterior. Ninguna tarea debe agregar tecnología, endpoint, campo o comportamiento que no esté definido en el Blueprint. Ante cualquier duda de diseño, la respuesta correcta ya existe en el Blueprint o en la Documentación Funcional — no inventar una nueva.

---

## Cómo usar este documento

1. Ejecutar las fases en orden estricto: 0 → 1 → 2 → … → 18.
2. Antes de empezar una fase, releer su bloque **Dependencias**.
3. Al completar una fase, verificar uno por uno los ítems de **Validaciones** y confirmar el **Criterio de finalización** antes de continuar.
4. Si una tarea de una fase requiere un dato que no está en este plan, buscarlo en el Blueprint (sección indicada entre paréntesis). No asumir, no improvisar, no rediseñar.
5. Cada fase está pensada para completarse en una única sesión de trabajo.

---

## Índice de fases

| Fase | Nombre | Resultado al finalizar |
|---|---|---|
| 0 | Preparación del entorno | Repositorio inicializado, Docker y entorno virtual listos |
| 1 | Proyecto FastAPI mínimo | La API responde en `/` y `/docs` |
| 2 | Estructura completa de carpetas y archivos | Todo el árbol de archivos existe, vacío pero importable |
| 3 | Persistencia — configuración y conexión | La app conecta a PostgreSQL sin errores |
| 4 | Enums | Los 4 enums definitivos existen y son importables |
| 5 | Entidades (modelos SQLAlchemy) | Las 6 tablas existen en la base de datos |
| 6 | Excepciones y manejo global de errores | Excepciones de dominio y handler 500 funcionando |
| 7 | DTOs (schemas Pydantic) | Todos los esquemas de entrada/salida validan correctamente |
| 8 | Servicio de parcelas (sincronización) | POST/PUT/DELETE funcionan a nivel de servicio (sin routers aún) |
| 9 | Routers de parcelas y estado | Contrato oficial con Croply expuesto y probado |
| 10 | Integración con Open-Meteo | El cliente obtiene datos climáticos reales |
| 11 | Módulos de sensores | Los 5 algoritmos de simulación calculan valores correctos |
| 12 | Servicio de eventos manuales | Eventos pendientes se aplican correctamente |
| 13 | Servicio de alertas | Las 5 reglas de alerta generan y resuelven alertas |
| 14 | Scheduler | El ciclo completo corre cada 25 minutos y persiste resultados |
| 15 | Endpoints internos restantes | Lecturas, eventos y controlador expuestos por HTTP |
| 16 | Frontend del simulador | Panel HTML funcional consumiendo la API |
| 17 | Docker y Docker Compose | El stack completo levanta con un solo comando |
| 18 | Pruebas finales y cierre | Todo el proyecto probado, limpio y coincidente con el Blueprint |

---

## Fase 0 — Preparación del entorno

### Objetivo
Dejar la máquina de desarrollo y el repositorio listos para empezar a programar.

### Dependencias
Ninguna. Es la primera fase.

### Tareas
1. Verificar que Python 3.11 o superior está instalado (`python --version`).
2. Verificar que Docker y Docker Compose (v2, comando `docker compose`) están instalados y corriendo.
3. Crear el directorio raíz del proyecto: `croply-iot-simulator/`.
4. Inicializar un repositorio Git dentro de ese directorio (`git init`).
5. Crear un entorno virtual de Python (`python -m venv venv`) dentro del proyecto.
6. Activar el entorno virtual.
7. Crear el archivo `requirements.txt` en la raíz, con las dependencias y versiones exactas indicadas en el Blueprint (sección 2 — Tecnologías y versiones). No agregar ninguna librería que no esté en esa lista.
8. Instalar las dependencias del `requirements.txt` en el entorno virtual.
9. Crear el archivo `.gitignore` con, como mínimo: `venv/`, `__pycache__/`, `*.pyc`, `.env`, `.pytest_cache/`.
10. Crear el archivo `.env.example` en la raíz, con las variables listadas en el Blueprint (sección 6 — Variables de entorno), usando valores de ejemplo (no reales).
11. Copiar `.env.example` a `.env` y completar `DATABASE_URL` apuntando a un host local (`localhost`) para esta fase.
12. Hacer el primer commit (`feat(init): inicializar estructura base del repositorio`).

### Archivos involucrados
- Crear: `requirements.txt`, `.gitignore`, `.env.example`, `.env`.
- Crear carpeta: `croply-iot-simulator/` (raíz).

### Resultado esperado
Un repositorio Git vacío de código pero con entorno virtual funcional, dependencias instaladas y variables de entorno definidas.

### Validaciones
- [ ] `python --version` devuelve 3.11 o superior.
- [ ] `docker compose version` responde sin error.
- [ ] El entorno virtual activa sin errores.
- [ ] `pip list` muestra exactamente las librerías del `requirements.txt`, sin librerías adicionales no solicitadas.
- [ ] `.env` existe y no está trackeado por Git (verificar con `git status`).

### Riesgos
- Instalar una versión de una librería distinta a la indicada en el Blueprint por no fijar la versión exacta con `==`. Evitarlo fijando siempre versión exacta en `requirements.txt`.
- Usar `docker-compose` (guion, binario standalone) en vez de `docker compose` (plugin v2). Verificar cuál está disponible antes de continuar a fases posteriores que usan Docker.

### Criterio de finalización
El entorno virtual existe, las dependencias del Blueprint están instaladas sin errores, y `.env`/`.env.example` existen con las variables correctas. No se continúa a la Fase 1 si `pip install` falló para alguna dependencia.

---

## Fase 1 — Proyecto FastAPI mínimo

### Objetivo
Tener una aplicación FastAPI que arranca y responde, antes de agregar cualquier lógica de negocio.

### Dependencias
Fase 0 completa (entorno virtual y dependencias instaladas).

### Tareas
1. Crear la carpeta `app/` con un archivo `__init__.py` vacío.
2. Crear `app/main.py` con una instancia mínima de `FastAPI()`.
3. Agregar un endpoint temporal `GET /` que devuelva un JSON simple (por ejemplo `{"status": "ok"}`). Este endpoint es solo de verificación y se eliminará o reemplazará en fases posteriores cuando se agregue `GET /status` (Blueprint, sección 9).
4. Arrancar la aplicación con Uvicorn en modo desarrollo, usando `APP_HOST` y `APP_PORT` de la Fase 0.
5. Verificar que `GET /` responde `200 OK`.
6. Verificar que la documentación automática de FastAPI carga correctamente en `/docs`.
7. Confirmar que los endpoints de este archivo se definen con `def`, no `async def` (Blueprint, sección 3 — Decisión: implementación síncrona).
8. Hacer commit (`feat(main): crear aplicación FastAPI mínima`).

### Archivos involucrados
- Crear: `app/__init__.py`, `app/main.py`.

### Resultado esperado
`uvicorn app.main:app --reload` arranca sin errores y responde en `/` y `/docs`.

### Validaciones
- [ ] `GET /` responde `200 OK` con el JSON esperado.
- [ ] `/docs` carga la interfaz Swagger sin errores en consola.
- [ ] No existe ningún `async def` en `main.py`.

### Riesgos
- Olvidar `--reload` no es un problema funcional, pero conviene usarlo en desarrollo para no reiniciar manualmente en cada fase.
- Confundir `APP_HOST`/`APP_PORT` de `.env` con valores hardcodeados. En esta fase es aceptable arrancar con valores fijos de línea de comando; la lectura desde variables de entorno se resuelve recién en la Fase 3 (`config.py`).

### Criterio de finalización
La aplicación arranca, responde en `/` y expone `/docs` correctamente. No se continúa a la Fase 2 si el servidor no arranca limpio.

---

## Fase 2 — Estructura completa de carpetas y archivos

### Objetivo
Crear el árbol de carpetas y archivos completo definido en el Blueprint (sección 4 — Estructura de carpetas), todos vacíos o con el mínimo contenido necesario para ser importables, antes de implementar ninguna lógica.

### Dependencias
Fase 1 completa.

### Tareas
1. Crear exactamente esta estructura de carpetas y archivos dentro de `app/` (Blueprint, sección 4):
   - `app/config.py`
   - `app/database.py`
   - `app/exceptions.py`
   - `app/models/` con `__init__.py` y los seis archivos: `parcela_simulada.py`, `controlador_simulado.py`, `sensor_simulado.py`, `lectura_sensor_simulada.py`, `alerta_simulada.py`, `evento_manual_pendiente.py`.
   - `app/schemas/` con `__init__.py` y los seis archivos: `parcela.py`, `sensor.py`, `controlador.py`, `lectura.py`, `evento.py`, `status.py`.
   - `app/routers/` con `__init__.py` y los seis archivos: `parcelas.py`, `estado.py`, `lecturas.py`, `eventos.py`, `controlador.py`, `status.py`.
   - `app/services/` con `__init__.py` y los cinco archivos: `parcela_service.py`, `scheduler_service.py`, `openmeteo_service.py`, `evento_service.py`, `alerta_service.py`.
   - `app/sensores/` con `__init__.py` y los seis archivos: `base.py`, `temp_hume_ambiental.py`, `radiacion_solar.py`, `precipitacion.py`, `humedad_suelo.py`, `ph.py`.
   - `app/enums/` con `__init__.py` y `enums.py`.
   - `app/static/` con un `index.html` de marcador de posición (`<html><body>Pendiente</body></html>`).
2. Crear la carpeta `migrations/` con la subcarpeta `versions/` (vacía por ahora; se completa con Alembic en la Fase 5).
3. Crear la carpeta `tests/` con `__init__.py`, `conftest.py` vacío, `test_parcelas.py`, `test_estado.py`, `test_scheduler.py` (todos vacíos por ahora) y la subcarpeta `tests/test_sensores/` con `__init__.py` y `test_temp_hume.py`, `test_radiacion.py`, `test_precipitacion.py`, `test_humedad_suelo.py`, `test_ph.py` (vacíos).
4. En cada archivo `.py` recién creado, dejar únicamente un comentario indicando su responsabilidad (por ejemplo, `# Modelo SQLAlchemy: ParcelaSimulada — ver Blueprint sección 7`), sin lógica todavía.
5. Verificar que no falta ningún archivo ni sobra ninguno respecto al árbol del Blueprint (sección 4).
6. Verificar que todos los paquetes (`models/`, `schemas/`, `routers/`, `services/`, `sensores/`, `enums/`) tienen su `__init__.py` y son importables desde `app.main` sin errores de import.
7. Hacer commit (`chore(estructura): crear árbol completo de carpetas y archivos base`).

### Archivos involucrados
Todos los listados en la tarea 1, 2 y 3. Ningún archivo fuera de ese árbol.

### Resultado esperado
El árbol de archivos del proyecto coincide exactamente con el Blueprint (sección 4), con todos los archivos vacíos o con comentario de responsabilidad, sin errores de import.

### Validaciones
- [ ] El árbol de carpetas coincide exactamente con el Blueprint, sin carpetas ni archivos de más o de menos.
- [ ] `python -c "import app.main"` no lanza `ImportError`.
- [ ] La aplicación de la Fase 1 sigue arrancando sin errores tras crear los archivos vacíos.

### Riesgos
- Agregar una carpeta no prevista (por ejemplo `repositories/` o `api/`) por costumbre de otros proyectos. El Blueprint no define esa capa: los servicios acceden directamente a la sesión de SQLAlchemy. No crear capas adicionales.
- Olvidar algún `__init__.py`, lo que rompe los imports de paquete.

### Criterio de finalización
Todo el árbol existe tal cual el Blueprint, es importable sin errores, y no hay ningún archivo o carpeta fuera de lo especificado. No se continúa a la Fase 3 si falta o sobra algo en la estructura.

---

## Fase 3 — Persistencia: configuración y conexión

### Objetivo
Tener la aplicación conectada a PostgreSQL, con la configuración leída desde variables de entorno, antes de definir ninguna tabla.

### Dependencias
Fase 2 completa (archivo `app/config.py` y `app/database.py` ya existen, vacíos).

### Tareas
1. En `app/config.py`, implementar la lectura de variables de entorno usando `python-dotenv` (Blueprint, sección 2) para cargar `.env`.
2. Definir en `app/config.py` una función o clase de configuración que exponga, como mínimo: `DATABASE_URL`, `SCHEDULER_INTERVAL_MINUTES`, `OPEN_METEO_BASE_URL`, `APP_HOST`, `APP_PORT`, `LOG_LEVEL`, `ENVIRONMENT` (Blueprint, sección 6).
3. En `app/database.py`, crear el `engine` de SQLAlchemy con `create_engine`, usando `DATABASE_URL` desde `config.py` (Blueprint, sección 19 — Persistencia, síncrono).
4. En `app/database.py`, crear `SessionLocal` con `sessionmaker`.
5. En `app/database.py`, crear la clase `Base` declarativa de SQLAlchemy (punto de partida para los modelos de la Fase 5).
6. En `app/database.py`, implementar la función `get_db()` exactamente como está definida en el Blueprint (sección 19), como dependencia de FastAPI (`yield` + `finally: db.close()`).
7. Configurar el módulo estándar `logging` (Blueprint, sección 18): formato de línea exacto (`%(asctime)s | %(levelname)-8s | %(name)s | %(message)s`), nivel leído desde `LOG_LEVEL`. Esta configuración puede vivir en `app/config.py` o invocarse desde `app/main.py` al arrancar.
8. Levantar un contenedor PostgreSQL local temporal (puede ser el mismo que se define en Docker en la Fase 17, o una instancia local para esta prueba) y verificar que `engine.connect()` no lanza excepción.
9. Hacer commit (`feat(persistencia): configurar conexión a base de datos y logging`).

### Archivos involucrados
- Modificar: `app/config.py`, `app/database.py`.
- Puede modificarse: `app/main.py` (si el logging se inicializa ahí).

### Resultado esperado
La aplicación puede abrir y cerrar una conexión a PostgreSQL sin errores, y la configuración se lee correctamente desde `.env`.

### Validaciones
- [ ] Un script o test manual que ejecute `engine.connect()` no lanza excepción.
- [ ] Cambiar un valor en `.env` (por ejemplo `LOG_LEVEL`) y confirmar que se refleja al reiniciar la app.
- [ ] `get_db()` se puede usar como dependencia de un endpoint de prueba sin errores.

### Riesgos
- Usar `psycopg2` en vez de `psycopg` (v3) en la cadena de conexión. El Blueprint especifica `psycopg` v3 síncrono (sección 2 y 3). Usar el prefijo correcto: `postgresql+psycopg://`.
- Hardcodear la cadena de conexión en `database.py` en vez de leerla desde `config.py`. Toda configuración pasa por `config.py`.

### Criterio de finalización
La conexión a PostgreSQL funciona de punta a punta usando las variables de entorno, y el logging está configurado con el formato exacto del Blueprint. No se continúa a la Fase 4 si la conexión falla.

---

## Fase 4 — Enums

### Objetivo
Definir los cuatro enums definitivos del sistema, exactamente como están cerrados en el Blueprint, antes de usarlos en ninguna entidad.

### Dependencias
Fase 2 completa (`app/enums/enums.py` existe, vacío).

### Tareas
1. En `app/enums/enums.py`, definir `TipoSensorEnum(str, Enum)` con exactamente los cinco valores del Blueprint (sección 5): `TEMP_HUME_AMBIENTAL`, `HUMEDAD_SUELO`, `RADIACION_SOLAR`, `PRECIPITACION`, `PH`.
2. Definir `EstadoTransmision(str, Enum)` con exactamente los dos valores: `TRANSMITIENDO`, `SIN_SEÑAL`.
3. Definir `TipoAlerta(str, Enum)` con exactamente los cinco valores: `HELADA`, `VWC_CRITICO`, `SATURACION`, `RIESGO_FUNGICO`, `ESTRES_HIDRICO`.
4. Definir `TipoEvento(str, Enum)` con exactamente los cinco valores: `RIEGO`, `HELADA`, `LLUVIA`, `DERIVA_PH`, `DESCONECTAR_NODO`.
5. No agregar ningún valor adicional a ninguno de los cuatro enums, ni alias, ni variantes.
6. Escribir un test rápido y descartable (o verificación manual en consola de Python) que importe los cuatro enums y confirme la cantidad exacta de valores de cada uno (5, 2, 5, 5 respectivamente).
7. Hacer commit (`feat(enums): definir los cuatro enums cerrados del sistema`).

### Archivos involucrados
- Modificar: `app/enums/enums.py`.

### Resultado esperado
Los cuatro enums existen, son importables desde `app.enums.enums`, y contienen exactamente los valores del Blueprint.

### Validaciones
- [ ] `len(list(TipoSensorEnum)) == 5`.
- [ ] `len(list(EstadoTransmision)) == 2`.
- [ ] `len(list(TipoAlerta)) == 5`.
- [ ] `len(list(TipoEvento)) == 5`.
- [ ] Ningún valor de ningún enum está en minúsculas ni con nombres distintos a los especificados.

### Riesgos
- Escribir `SIN_SEÑAL` sin la Ñ o con guion en vez de guion bajo. Debe coincidir carácter por carácter con el Blueprint.
- Heredar de `Enum` en vez de `(str, Enum)`. El Blueprint especifica `(str, Enum)` para que los valores se serialicen directamente como string en JSON.

### Criterio de finalización
Los cuatro enums existen con los valores exactos y son importables sin errores. No se continúa a la Fase 5 si algún valor no coincide con el Blueprint.

---

## Fase 5 — Entidades (modelos SQLAlchemy) y migraciones

### Objetivo
Definir las seis tablas del simulador y dejarlas creadas en la base de datos mediante Alembic.

### Dependencias
Fase 3 completa (conexión y `Base` disponibles) y Fase 4 completa (enums disponibles).

### Tareas
1. En `app/models/parcela_simulada.py`, definir la clase `ParcelaSimulada` heredando de `Base`, con exactamente los campos del Blueprint (sección 7): `parcela_id` (PK, int, sin autoincrement), `nombre`, `latitud`, `longitud`, `activa` (bool, default `True`), `creada_en` (timestamp UTC).
2. En `app/models/controlador_simulado.py`, definir `ControladorSimulado`: `controlador_id` (PK, int, sin autoincrement), `parcela_id` (FK a `parcelas_simuladas`, `ON DELETE CASCADE`), `ip_controlador` (nullable), `estado` (`EstadoTransmision`, default `TRANSMITIENDO`).
3. En `app/models/sensor_simulado.py`, definir `SensorSimulado`: `sensor_id` (PK, int, sin autoincrement), `controlador_id` (FK CASCADE), `parcela_id` (FK CASCADE, desnormalizado), `tipo` (`TipoSensorEnum`), `ip_sensor` (nullable), `ultimo_valor` (float, nullable), `fecha_ultima_lectura` (timestamp, nullable), `vwc_actual` (float, nullable), `kc` (float, nullable, default `0.4`), `profundidad_radicular` (float, nullable, default `0.4`), `ph_base` (float, nullable, default `6.5`).
4. En `app/models/lectura_sensor_simulada.py`, definir `LecturaSensorSimulada`: `id` (PK bigint autoincrement), `sensor_id` (FK CASCADE), `parcela_id` (FK CASCADE, desnormalizado), `tipo_sensor` (varchar, desnormalizado), `valor` (float), `unidad` (varchar), `timestamp` (timestamp UTC).
5. En `app/models/alerta_simulada.py`, definir `AlertaSimulada`: `id` (PK), `parcela_id` (FK CASCADE), `tipo` (`TipoAlerta`), `valor_disparador` (float), `resuelta` (bool, default `False`), `timestamp`.
6. En `app/models/evento_manual_pendiente.py`, definir `EventoManualPendiente`: `id` (PK), `parcela_id` (FK CASCADE), `tipo_evento` (`TipoEvento`), `parametros` (JSONB, default `{}`), `aplicado` (bool, default `False`), `creado_en` (timestamp UTC).
7. Definir los nombres de tabla exactamente como en el Blueprint (sección 5): `parcelas_simuladas`, `controladores_simulados`, `sensores_simulados`, `lecturas_simuladas`, `alertas_simuladas`, `eventos_manuales_pendientes`.
8. Inicializar Alembic en la carpeta `migrations/` (`alembic init` apuntando a esa carpeta, o configurar `alembic.ini` para que use `migrations/` en vez de `alembic/` por defecto).
9. Configurar `migrations/env.py` para que apunte a `Base.metadata` de `app/database.py`, de forma que Alembic detecte automáticamente los seis modelos.
10. Generar la migración inicial (`alembic revision --autogenerate -m "crear tablas iniciales"`).
11. Revisar manualmente el archivo de migración generado y agregar los cinco índices definidos en el Blueprint (sección 8): `idx_parcelas_activa`, `idx_sensores_parcela`, `idx_eventos_pendientes` (parcial, `WHERE aplicado = false`), `idx_alertas_activas` (parcial, `WHERE resuelta = false`), `idx_lecturas_sensor_timestamp` (compuesto, sobre `lecturas_simuladas(sensor_id, timestamp DESC)`).
12. Agregar en la misma migración el índice compuesto `idx_lecturas_sensor_timestamp` sobre `lecturas_simuladas(sensor_id, timestamp DESC)` (Blueprint, sección 8). No usar ninguna extensión de series temporales: la base de datos es PostgreSQL estándar.
13. Ejecutar `alembic upgrade head` contra la base de datos local y verificar que las seis tablas y los cinco índices se crearon.
14. Hacer commit (`feat(modelos): definir entidades SQLAlchemy y migración inicial`).

### Archivos involucrados
- Modificar: los seis archivos de `app/models/`.
- Crear/modificar: `migrations/env.py`, `migrations/versions/<primera_migración>.py`, `alembic.ini`.

### Resultado esperado
Las seis tablas existen en PostgreSQL con sus columnas, claves foráneas, valores por defecto e índices exactamente como en el Blueprint.

### Validaciones
- [ ] `alembic upgrade head` corre sin errores.
- [ ] Las seis tablas existen (verificar con `\dt` en `psql` o herramienta equivalente).
- [ ] Los cinco índices existen (verificar con `\di`).
- [ ] Los `ON DELETE CASCADE` están efectivamente configurados en las claves foráneas (probar borrando una fila padre y confirmar que las hijas se eliminan).
- [ ] Ningún modelo genera IDs autoincrementales para `parcela_id`, `controlador_id` o `sensor_id` (Blueprint, decisión cerrada: IDs vienen de Croply).

### Riesgos
- Dejar que SQLAlchemy/Alembic autogenere `parcela_id`/`controlador_id`/`sensor_id` como `SERIAL`. Estos tres campos deben ser `INTEGER PRIMARY KEY` sin autoincrement, porque siempre los provee Croply.
- Olvidar el `ON DELETE CASCADE` en alguna FK, lo que rompería el comportamiento de eliminación en cascada ya cerrado en la documentación funcional.
- No revisar la migración autogenerada y perder los índices parciales (`WHERE aplicado = false` / `WHERE resuelta = false`), que Alembic no siempre autogenera correctamente.

### Criterio de finalización
Las seis tablas existen en la base de datos, con índices y relaciones correctas, y la migración queda versionada en `migrations/versions/`. No se continúa a la Fase 6 si alguna tabla, índice o relación no coincide con el Blueprint.

---

## Fase 6 — Excepciones y manejo global de errores

### Objetivo
Tener las excepciones de dominio y el manejo global de errores listos antes de escribir cualquier endpoint real.

### Dependencias
Fase 2 completa (`app/exceptions.py` existe, vacío).

### Tareas
1. En `app/exceptions.py`, definir las excepciones de dominio indicadas en el Blueprint (sección 17): `ParcelaNoEncontradaError`, `ParcelaYaExisteError`, `OpenMeteoError`, `SensorTipoDesconocidoError`. Cada una hereda de `Exception` (o de una excepción base común definida en el mismo archivo).
2. En `app/main.py`, registrar un manejador de excepciones global (`@app.exception_handler`) que capture cualquier excepción no controlada y devuelva `500`, sin exponer el traceback en la respuesta (Blueprint, sección 10 y 17).
3. Registrar manejadores específicos (o lógica equivalente dentro de los routers en fases posteriores) para traducir `ParcelaNoEncontradaError` → `404`, y `ParcelaYaExisteError` → `409`, según el catálogo de errores del Blueprint (sección 10).
4. Verificar que un endpoint de prueba que lance `ParcelaNoEncontradaError` efectivamente devuelve `404` y no `500`.
5. Hacer commit (`feat(errores): definir excepciones de dominio y handler global`).

### Archivos involucrados
- Modificar: `app/exceptions.py`, `app/main.py`.

### Resultado esperado
Las excepciones de dominio existen y cualquier error no controlado responde `500` sin traceback expuesto; los errores de negocio ya mapean a los códigos HTTP correctos.

### Validaciones
- [ ] Lanzar manualmente cada una de las cuatro excepciones desde un endpoint de prueba y verificar el código HTTP resultante.
- [ ] Confirmar que el cuerpo de una respuesta `500` no incluye stack trace ni detalles internos.

### Riesgos
- Dejar que FastAPI devuelva el traceback por defecto en modo debug. Verificar que el modo debug está desactivado según `ENVIRONMENT` de `.env`.

### Criterio de finalización
Las cuatro excepciones de dominio existen y el manejo de errores traduce correctamente a los códigos HTTP del Blueprint. No se continúa a la Fase 7 si algún error de negocio sigue devolviendo `500`.

---

## Fase 7 — DTOs (schemas Pydantic)

### Objetivo
Definir todos los esquemas de entrada y salida HTTP exactamente como en el Blueprint, antes de escribir servicios o routers que los usen.

### Dependencias
Fase 4 completa (enums disponibles para usar en los schemas).

### Tareas
1. En `app/schemas/parcela.py`, definir los schemas Pydantic para el body de `POST /parcelas` y `PUT /parcelas/{id}`, replicando exactamente la estructura anidada del Blueprint (sección 9): objeto `parcela` con `id`, `nombre`, `latitud`, `longitud` y `controlador` anidado (`id`, `ip`, `estado`, `sensores` con `id` y `tipo`).
2. En `app/schemas/sensor.py`, definir el schema de sensor usado dentro del DTO de parcela y, si corresponde, el schema de sensor usado en la respuesta de `GET /parcelas/{id}/estado`.
3. En `app/schemas/controlador.py`, definir el schema de controlador para el DTO de entrada y el schema usado en `PATCH /parcelas/{id}/controlador`.
4. En `app/schemas/lectura.py`, definir el schema de respuesta de `GET /parcelas/{id}/lecturas`.
5. En `app/schemas/evento.py`, definir el schema de entrada de `POST /parcelas/{id}/eventos` (`tipo`, `parametros`).
6. En `app/schemas/status.py`, definir el schema de respuesta de `GET /status` (`scheduler_activo`, `ultima_ejecucion`, `proxima_ejecucion`, `parcelas_activas`).
7. Definir también el schema de respuesta de `GET /parcelas/{id}/estado` (Blueprint, sección 9), pudiendo ubicarlo en `app/schemas/parcela.py` o `app/schemas/sensor.py` según corresponda a su contenido.
8. Agregar las validaciones de tipo y enum correspondientes en cada schema (por ejemplo, `tipo` debe ser un `TipoSensorEnum` válido, `estado` debe ser un `EstadoTransmision` válido).
9. Escribir un test rápido (o verificación manual) que intente construir cada schema con el JSON de ejemplo exacto del Blueprint (sección 9) y confirme que valida sin errores.
10. Escribir un test rápido que intente construir el DTO principal con un `tipo` de sensor inválido y confirme que Pydantic lo rechaza.
11. Hacer commit (`feat(schemas): definir DTOs de entrada y salida según contrato REST`).

### Archivos involucrados
- Modificar: los seis archivos de `app/schemas/`.

### Resultado esperado
Todos los DTOs de entrada y salida existen y validan exactamente los ejemplos JSON del Blueprint.

### Validaciones
- [ ] El JSON de ejemplo de `POST /parcelas` (Blueprint, sección 9) valida sin errores contra el schema correspondiente.
- [ ] El JSON de ejemplo de `GET /parcelas/{id}/estado` valida sin errores.
- [ ] El JSON de ejemplo de `POST /parcelas/{id}/eventos` valida sin errores.
- [ ] El JSON de ejemplo de `GET /status` valida sin errores.
- [ ] Un `tipo` de sensor inválido (por ejemplo `"HUMEDAD"`) es rechazado por el schema.

### Riesgos
- Definir un DTO "parcial" para actualizaciones. No existen actualizaciones parciales: `PUT` usa exactamente el mismo schema que `POST` (Blueprint, sección 9).
- Exponer en algún DTO de salida un campo interno del simulador que no forme parte del contrato (por ejemplo `vwc_actual`, `kc`, `ph_base`). Ningún DTO expone esos campos.

### Criterio de finalización
Todos los schemas existen y validan correctamente los ejemplos del Blueprint, incluyendo casos inválidos. No se continúa a la Fase 8 si algún schema no coincide exactamente con el JSON de ejemplo del Blueprint.

---

## Fase 8 — Servicio de parcelas (sincronización)

### Objetivo
Implementar la lógica de alta, reemplazo completo y baja de una parcela a nivel de servicio, sin exponerla todavía por HTTP.

### Dependencias
Fase 5 completa (modelos y BD), Fase 6 completa (excepciones), Fase 7 completa (DTOs).

### Tareas
1. En `app/services/parcela_service.py`, implementar una función `crear_parcela(db, dto)` que reciba el DTO validado y cree en una única transacción: la fila de `ParcelaSimulada`, la fila de `ControladorSimulado` y las filas de `SensorSimulado` correspondientes, conservando exactamente los IDs recibidos.
2. Implementar el chequeo de existencia previa: si el `parcela_id` ya existe, lanzar `ParcelaYaExisteError` (definida en la Fase 6) antes de intentar el insert.
3. Implementar `reemplazar_configuracion(db, parcela_id, dto)`: si la parcela no existe, lanzar `ParcelaNoEncontradaError`; si existe, eliminar las filas de `ControladorSimulado`/`SensorSimulado` asociadas e insertar las nuevas a partir del DTO, en una única transacción, sin comparar contra la configuración anterior (Blueprint, sección 23, DP-01 — confirmar este comportamiento antes de dar la fase por cerrada, ver bloque de Riesgos).
4. Implementar `eliminar_parcela(db, parcela_id)`: si no existe, lanzar `ParcelaNoEncontradaError`; si existe, eliminar la fila de `ParcelaSimulada` y confiar en `ON DELETE CASCADE` para el resto.
5. Asegurar que las tres funciones hacen `commit()` al final y `rollback()` si ocurre cualquier error durante la transacción.
6. Escribir tests (pueden ir en `tests/test_parcelas.py`, ya que todavía no hay router) que ejerciten las tres funciones directamente contra una base de datos de test: alta exitosa, alta duplicada, reemplazo exitoso, reemplazo de parcela inexistente, baja exitosa, baja de parcela inexistente.
7. Hacer commit (`feat(servicios): implementar sincronización de parcelas (alta, reemplazo, baja)`).

### Archivos involucrados
- Modificar: `app/services/parcela_service.py`.
- Modificar: `tests/test_parcelas.py` (tests a nivel de servicio, sin HTTP todavía).

### Resultado esperado
Las tres operaciones de sincronización funcionan correctamente contra la base de datos real, incluyendo sus casos de error, sin que exista todavía ningún endpoint HTTP que las exponga.

### Validaciones
- [ ] Crear una parcela con datos de ejemplo del Blueprint y confirmar que las tablas `parcelas_simuladas`, `controladores_simulados` y `sensores_simulados` quedan pobladas correctamente.
- [ ] Intentar crear la misma parcela dos veces y confirmar que la segunda vez lanza `ParcelaYaExisteError`.
- [ ] Reemplazar la configuración de una parcela existente quitando un sensor y confirmar que el sensor eliminado y su historial (si existiera) desaparecen por cascada.
- [ ] Eliminar una parcela y confirmar que no quedan filas huérfanas en ninguna tabla dependiente.

### Riesgos
- Implementar lógica de comparación/diffing entre la configuración vieja y la nueva en el `PUT`. El Blueprint es explícito: se reemplaza todo sin detectar diferencias.
- **DP-01 pendiente (Blueprint, sección 23):** el comportamiento de "sensores nuevos se crean, sensores faltantes se eliminan con su historial" está definido en el Blueprint pero marcado como pendiente de confirmación con el equipo. Implementar tal como está escrito en el Blueprint; si posteriormente se confirma un comportamiento distinto, actualizar esta fase y no versiones futuras del código de forma aislada.

### Criterio de finalización
Las tres funciones de servicio pasan todos sus tests contra la base de datos real, incluyendo los casos de error. No se continúa a la Fase 9 si alguna transacción deja datos inconsistentes ante un fallo simulado.

---

## Fase 9 — Routers de parcelas y estado (contrato oficial con Croply)

### Objetivo
Exponer por HTTP los cuatro endpoints del contrato oficial con Croply: `POST /parcelas`, `PUT /parcelas/{id}`, `DELETE /parcelas/{id}`, `GET /parcelas/{id}/estado`.

### Dependencias
Fase 8 completa (servicio de parcelas funcionando).

### Tareas
1. En `app/routers/parcelas.py`, crear un `APIRouter` e implementar `POST /parcelas`, invocando `parcela_service.crear_parcela`, devolviendo `201` en éxito.
2. Implementar `PUT /parcelas/{id}`, invocando `parcela_service.reemplazar_configuracion`, devolviendo `200` en éxito.
3. Implementar `DELETE /parcelas/{id}`, invocando `parcela_service.eliminar_parcela`, devolviendo `200` en éxito (Blueprint, sección 10 — tabla de endpoints).
4. En `app/routers/estado.py`, implementar `GET /parcelas/{id}/estado`, leyendo directamente desde `SensorSimulado` (`ultimo_valor`, `fecha_ultima_lectura`), armando la respuesta con la forma exacta del Blueprint (sección 9). Nunca debe consultar `LecturaSensorSimulada`.
5. Incluir ambos routers en `app/main.py` (`app.include_router(...)`).
6. Eliminar el endpoint temporal `GET /` de la Fase 1 si ya no es necesario (o dejarlo como simple healthcheck, a criterio, sin que forme parte del contrato).
7. Probar manualmente los cuatro endpoints desde `/docs` (Swagger UI) con los ejemplos del Blueprint.
8. Completar `tests/test_parcelas.py` con tests de integración usando `TestClient` de FastAPI: alta exitosa (`201`), alta duplicada (`409`), reemplazo exitoso (`200`), reemplazo de parcela inexistente (`404`), baja exitosa (`200`), baja de parcela inexistente (`404`), validación de body inválido (`422`).
9. Completar `tests/test_estado.py`: consulta de estado antes del primer ciclo del scheduler (campos `valor_actual`/`fecha_ultima_lectura` en `null`), consulta de estado de parcela inexistente (`404`).
10. Hacer commit (`feat(routers): exponer contrato REST oficial con Croply`).

### Archivos involucrados
- Modificar: `app/routers/parcelas.py`, `app/routers/estado.py`, `app/main.py`.
- Modificar: `tests/test_parcelas.py`, `tests/test_estado.py`.

### Resultado esperado
Los cuatro endpoints del contrato oficial funcionan de punta a punta contra la base de datos real y están cubiertos por tests de integración.

### Validaciones
- [ ] Los cuatro endpoints responden con los códigos HTTP exactos del Blueprint (sección 10).
- [ ] `GET /parcelas/{id}/estado` sobre una parcela recién creada (sin ciclos del scheduler todavía) devuelve `valor_actual` y `fecha_ultima_lectura` en `null`, sin error.
- [ ] Todos los tests de `test_parcelas.py` y `test_estado.py` pasan con `pytest`.

### Riesgos
- Exponer accidentalmente un endpoint parcial (por ejemplo, agregar un sensor sin reemplazar toda la configuración). El contrato solo admite `PUT` con configuración completa.
- Que `GET /estado` consulte por error `LecturaSensorSimulada` en vez de `SensorSimulado`. Esto rompe una decisión cerrada explícita del Blueprint y de la Documentación Funcional.

### Criterio de finalización
Los cuatro endpoints del contrato oficial pasan todos sus tests de integración. No se continúa a la Fase 10 si alguno de los cuatro endpoints no cumple exactamente los códigos HTTP y la forma de respuesta del Blueprint.

---

## Fase 10 — Integración con Open-Meteo

### Objetivo
Tener un cliente que, dado latitud y longitud, devuelva las variables climáticas necesarias para los sensores.

### Dependencias
Fase 6 completa (`OpenMeteoError` disponible). No depende de fases de sensores ni scheduler.

### Tareas
1. En `app/services/openmeteo_service.py`, implementar una función `obtener_clima_actual(latitud, longitud)` que use `httpx.Client` síncrono (Blueprint, sección 3 y 13).
2. Construir la URL exacta indicada en el Blueprint (sección 13), incluyendo las variables `current`: `temperature_2m`, `relative_humidity_2m`, `shortwave_radiation`, `precipitation`, `cloud_cover`, `wind_speed_10m`, con `timezone=UTC`.
3. Configurar el timeout del cliente en 10 segundos (Blueprint, sección 13).
4. Mapear la respuesta JSON de Open-Meteo a un diccionario o estructura interna simple con esas seis variables, ya tipadas como `float`.
5. Si la petición falla (timeout, error de red, respuesta HTTP no exitosa, o variables faltantes en la respuesta), lanzar `OpenMeteoError` (no devolver valores parciales ni inventados).
6. Escribir tests en `tests/` (puede integrarse a `tests/test_scheduler.py` más adelante, o crear un archivo dedicado si se prefiere) que mockeen la respuesta HTTP con `unittest.mock` (Blueprint, sección 20) y verifiquen: mapeo correcto en caso exitoso, y `OpenMeteoError` en caso de timeout o respuesta con variables faltantes.
7. Hacer commit (`feat(openmeteo): implementar cliente HTTP síncrono hacia Open-Meteo`).

### Archivos involucrados
- Modificar: `app/services/openmeteo_service.py`.

### Resultado esperado
La función `obtener_clima_actual` devuelve datos climáticos reales dado un par de coordenadas, y lanza `OpenMeteoError` de forma controlada ante cualquier fallo.

### Validaciones
- [ ] Una llamada real (o mockeada) con coordenadas válidas devuelve las seis variables esperadas, todas como `float`.
- [ ] Un mock de timeout resulta en `OpenMeteoError`, no en una excepción no controlada.
- [ ] Un mock de respuesta con una variable faltante resulta en `OpenMeteoError`.

### Riesgos
- Usar `httpx.AsyncClient` en vez de `httpx.Client`. El Blueprint es explícito: cliente síncrono (sección 3).
- No poner límite de timeout, lo que podría colgar un ciclo completo del scheduler si Open-Meteo no responde.

### Criterio de finalización
El cliente de Open-Meteo funciona correctamente en el caso exitoso y en los casos de error, con tests que lo confirman. No se continúa a la Fase 11 si el manejo de errores no está probado.

---

## Fase 11 — Módulos de sensores

### Objetivo
Implementar los cinco algoritmos de simulación, cada uno desacoplado del resto, según las fórmulas exactas del Blueprint.

### Dependencias
Fase 4 completa (enums), Fase 5 completa (modelo `SensorSimulado` con sus campos de estado persistente).

### Tareas
1. En `app/sensores/base.py`, definir la firma común que deben respetar todos los módulos de sensor: `calcular_valor(datos_clima, sensor, evento, contexto) -> tuple[float, str]` (Blueprint, sección 12). Puede definirse como interfaz/abstract base o simplemente como convención documentada en el archivo, según se prefiera, pero la firma debe ser idéntica en los cinco módulos.
2. Implementar `app/sensores/temp_hume_ambiental.py` exactamente según la fórmula del Blueprint (sección 12): cálculo de temperatura con ruido gaussiano, humedad relativa con clamp 0-100, cálculo de VPD guardado en `contexto`, y el efecto del evento `HELADA` (resta 2.0 al último valor).
3. Implementar `app/sensores/radiacion_solar.py` según la fórmula del Blueprint: radiación ajustada por nubosidad y ruido gaussiano, cálculo de ETo guardado en `contexto`.
4. Implementar `app/sensores/precipitacion.py` según la fórmula del Blueprint: cálculo de mm por intervalo, pulsos, mm efectivos, lluvia efectiva guardada en `contexto`, y el efecto del evento `LLUVIA` (suma `parametros["mm"]`).
5. Implementar `app/sensores/humedad_suelo.py` según la fórmula del Blueprint: inicialización de VWC en 30.0 si `vwc_actual` es `None`, cálculo de VWC usando `ETo` y `lluvia_efectiva` del `contexto`, persistencia de `vwc_actual` en el sensor, clamp 0-100, y el efecto del evento `RIEGO` (suma `parametros["mm"]` a la lluvia efectiva antes del cálculo).
6. Implementar `app/sensores/ph.py` según la fórmula del Blueprint: deriva lineal por días, variación senoidal diurna, ruido gaussiano, clamp 0-14.
7. Confirmar que cada módulo respeta el orden de dependencia de datos entre sensores (temperatura/HR antes que radiación, radiación antes que humedad de suelo) mediante el uso correcto de `contexto` como mecanismo de paso de datos entre sensores dentro de un mismo ciclo (no hace falta orquestar esto todavía; se resuelve en la Fase 14, pero cada módulo debe leer/escribir el `contexto` según lo definido en el Blueprint).
8. Escribir los tests unitarios en `tests/test_sensores/`, uno por módulo, con datos de clima fijos y semilla aleatoria fija (o verificación de rango, no de valor exacto, dado el ruido gaussiano), según el Blueprint (sección 20).
9. Escribir un test específico para `humedad_suelo.py` que confirme la persistencia de `vwc_actual` entre dos llamadas sucesivas (simulando dos ciclos).
10. Escribir un test específico para cada sensor que confirme el efecto de su evento manual asociado (`HELADA`, `LLUVIA`, `RIEGO`).
11. Hacer commit (`feat(sensores): implementar los cinco algoritmos de simulación`).

### Archivos involucrados
- Modificar: los seis archivos de `app/sensores/`.
- Modificar: los cinco archivos de `tests/test_sensores/`.

### Resultado esperado
Los cinco módulos de sensor calculan valores correctos y dentro de rango, de forma completamente aislada (sin base de datos, sin HTTP), y los tests unitarios lo confirman.

### Validaciones
- [ ] Cada test unitario pasa con `pytest`.
- [ ] Los valores de humedad relativa y VWC nunca salen del rango 0-100 en ningún test, incluso con entradas extremas.
- [ ] El valor de pH nunca sale del rango 0-14.
- [ ] `humedad_suelo.py` conserva correctamente `vwc_actual` entre llamadas sucesivas dentro del mismo test.

### Riesgos
- Testear valores exactos en sensores con ruido gaussiano, lo que hace los tests no determinísticos. Fijar semilla aleatoria o testear rangos, no igualdad exacta (Blueprint, sección 20).
- Implementar el orden de cálculo (temperatura → radiación → humedad de suelo) de forma incorrecta dentro de un mismo módulo. El orden real entre sensores se resuelve en el scheduler (Fase 14); en esta fase cada módulo solo debe leer/escribir correctamente el `contexto` recibido.
- No aplicar el clamp de rango correspondiente a cada sensor, generando valores fuera de rango físicamente imposibles.

### Criterio de finalización
Los cinco módulos de sensor pasan todos sus tests unitarios de forma aislada. No se continúa a la Fase 12 si algún sensor produce valores fuera de rango o no respeta la fórmula del Blueprint.

---

## Fase 12 — Servicio de eventos manuales

### Objetivo
Implementar la lógica de aplicación de eventos manuales pendientes, antes de integrarla al scheduler.

### Dependencias
Fase 5 completa (modelo `EventoManualPendiente`), Fase 4 completa (`TipoEvento`).

### Tareas
1. En `app/services/evento_service.py`, implementar una función que consulte el evento pendiente más antiguo (`aplicado = False`) de una parcela dada (Blueprint, sección 11 y 14).
2. Implementar una función que cree un nuevo `EventoManualPendiente` a partir del DTO de entrada (para uso posterior del router de eventos en la Fase 15).
3. Implementar una función que marque un evento como `aplicado = True` después de que el scheduler lo haya procesado (esto se invoca desde la Fase 14, pero la función se define acá).
4. Confirmar que solo se considera un evento pendiente por parcela por ciclo (el más antiguo), tal como está definido en el Blueprint (sección 11, paso 2).
5. Escribir tests que verifiquen: creación de un evento, consulta del evento pendiente más antiguo cuando hay varios encolados, marcado como aplicado y que deja de aparecer como pendiente.
6. Hacer commit (`feat(eventos): implementar servicio de eventos manuales pendientes`).

### Archivos involucrados
- Modificar: `app/services/evento_service.py`.

### Resultado esperado
El servicio de eventos permite crear, consultar el más antiguo pendiente y marcar como aplicado, listo para ser usado por el scheduler en la Fase 14 y por el router en la Fase 15.

### Validaciones
- [ ] Crear dos eventos para la misma parcela y confirmar que la consulta del "más antiguo pendiente" devuelve el correcto según `creado_en`.
- [ ] Marcar un evento como aplicado y confirmar que ya no aparece en la consulta de pendientes.

### Riesgos
- Aplicar más de un evento pendiente por parcela en un mismo ciclo. El Blueprint especifica solo el más antiguo por ciclo (sección 11).

### Criterio de finalización
El servicio de eventos pasa todos sus tests de forma aislada, sin todavía estar conectado al scheduler ni a ningún router HTTP. No se continúa a la Fase 13 si el orden de aplicación (más antiguo primero) no está garantizado.

---

## Fase 13 — Servicio de alertas

### Objetivo
Implementar las cinco reglas de alerta interna, antes de integrarlas al scheduler.

### Dependencias
Fase 5 completa (modelo `AlertaSimulada`), Fase 4 completa (`TipoAlerta`).

### Tareas
1. En `app/services/alerta_service.py`, implementar la regla `HELADA`: se activa si la temperatura es menor a 2°C, se resuelve si es mayor o igual a 2°C (Blueprint, sección 15).
2. Implementar la regla `VWC_CRITICO`: se activa si VWC < 15%, se resuelve si VWC ≥ 15%.
3. Implementar la regla `SATURACION`: se activa si VWC > 60%, se resuelve si VWC ≤ 60%.
4. Implementar la regla `RIESGO_FUNGICO`: se activa si HR > 80% y temperatura entre 15-25°C durante 2 o más ciclos consecutivos; se resuelve cuando la condición deja de cumplirse.
5. Implementar la regla `ESTRES_HIDRICO`: se activa si VPD > 1.8 kPa, se resuelve si VPD ≤ 1.8 kPa.
6. Implementar la lógica de no duplicar alertas activas: si ya existe una alerta activa (`resuelta = False`) del mismo tipo para la misma parcela, no crear una nueva.
7. Implementar la lógica de resolución automática: cuando la condición deja de cumplirse en un ciclo posterior, marcar la alerta existente como `resuelta = True`.
8. Escribir tests para cada una de las cinco reglas, con valores justo por debajo y por encima de cada umbral, y un test específico que confirme que no se duplican alertas activas del mismo tipo.
9. Hacer commit (`feat(alertas): implementar las cinco reglas de alertas internas`).

### Archivos involucrados
- Modificar: `app/services/alerta_service.py`.

### Resultado esperado
Las cinco reglas generan y resuelven alertas correctamente, sin duplicados, listas para ser invocadas desde el scheduler en la Fase 14.

### Validaciones
- [ ] Cada una de las cinco reglas pasa sus tests de umbral (justo por debajo y por encima).
- [ ] Una condición sostenida durante varios ciclos no genera alertas duplicadas.
- [ ] Una alerta activa se marca `resuelta = True` cuando la condición deja de cumplirse en un test simulando dos ciclos.

### Riesgos
- Olvidar el requisito de "2 o más ciclos consecutivos" en `RIESGO_FUNGICO`, generando la alerta con un solo ciclo de HR/temperatura elevadas.
- Generar una alerta duplicada por no verificar si ya existe una activa del mismo tipo antes de insertar.

### Criterio de finalización
Las cinco reglas pasan todos sus tests de forma aislada, incluyendo los casos de no duplicación y resolución. No se continúa a la Fase 14 si alguna regla no respeta exactamente el umbral o la condición de resolución del Blueprint.

---

## Fase 14 — Scheduler

### Objetivo
Implementar el ciclo completo de simulación, orquestando Open-Meteo, sensores, eventos y alertas, ejecutándose automáticamente cada 25 minutos.

### Dependencias
Fase 10 completa (Open-Meteo), Fase 11 completa (sensores), Fase 12 completa (eventos), Fase 13 completa (alertas), Fase 9 completa (persistencia de `SensorSimulado`/`LecturaSensorSimulada` accesible).

### Tareas
1. En `app/services/scheduler_service.py`, configurar un `BackgroundScheduler` de APScheduler con `IntervalTrigger(minutes=25)`, usando `SCHEDULER_INTERVAL_MINUTES` desde `config.py` (Blueprint, sección 11).
2. Implementar la función del ciclo completo, respetando exactamente el orden obligatorio del Blueprint (sección 11):
   a. Obtener las parcelas con `activa = True` y controlador en `TRANSMITIENDO`.
   b. Para cada parcela: cargar el evento pendiente más antiguo (Fase 12), si existe.
   c. Llamar a Open-Meteo (Fase 10); si falla, registrar `WARNING` y omitir esa parcela, continuando con las demás.
   d. Inicializar `contexto = {}`.
   e. Para cada sensor de la parcela: invocar `calcular_valor(datos_clima, sensor, evento, contexto)` del módulo correspondiente (Fase 11), actualizar `ultimo_valor`/`fecha_ultima_lectura` en `SensorSimulado`, e insertar la fila correspondiente en `LecturaSensorSimulada`.
   f. Evaluar las reglas de `alerta_service` (Fase 13) sobre los valores recién calculados.
   g. Marcar el evento (si había uno) como `aplicado = True`.
   h. Hacer `commit()` de la parcela; si falla, hacer `rollback()` solo de esa parcela, registrar `ERROR` y continuar con las demás parcelas del ciclo.
3. Registrar el inicio del scheduler en el evento `startup` de `app/main.py`, y su detención en el evento `shutdown`.
4. Implementar en `scheduler_service.py` las funciones o atributos necesarios para exponer `scheduler_activo`, `ultima_ejecucion` y `proxima_ejecucion`, que se usarán en el endpoint `GET /status` de la Fase 15.
5. Agregar un mecanismo para poder disparar manualmente un ciclo del scheduler desde un test (sin esperar los 25 minutos reales), para poder probarlo de punta a punta.
6. Completar `tests/test_scheduler.py`: un ciclo completo con Open-Meteo mockeado, verificando que se actualiza `ultimo_valor`, se inserta una `LecturaSensorSimulada` por sensor, se aplican eventos pendientes, se generan alertas cuando corresponde, y que una parcela con error de Open-Meteo no interrumpe el procesamiento de las demás.
7. Hacer commit (`feat(scheduler): implementar ciclo completo de simulación cada 25 minutos`).

### Archivos involucrados
- Modificar: `app/services/scheduler_service.py`, `app/main.py`.
- Modificar: `tests/test_scheduler.py`.

### Resultado esperado
El ciclo completo de simulación corre automáticamente cada 25 minutos (y puede dispararse manualmente en tests), actualizando estado, historial y alertas, sin que el fallo de una parcela afecte a las demás.

### Validaciones
- [ ] Disparar un ciclo manual en un test y confirmar que `SensorSimulado.ultimo_valor` y `fecha_ultima_lectura` se actualizan para los cinco sensores de una parcela de prueba.
- [ ] Confirmar que se insertan cinco filas nuevas en `LecturaSensorSimulada` por cada ciclo, una por sensor.
- [ ] Simular un fallo de Open-Meteo para una parcela entre varias, y confirmar que las demás parcelas del mismo ciclo se procesan igual.
- [ ] Confirmar que un evento manual pendiente se aplica y queda marcado `aplicado = True` tras el ciclo.
- [ ] Confirmar que una condición de alerta genera la fila correspondiente en `AlertaSimulada`.

### Riesgos
- Que un error en una parcela detenga el ciclo completo. El Blueprint exige aislar el `commit`/`rollback` por parcela (sección 11, paso 8).
- Ejecutar el scheduler dos veces en paralelo si la app se reinicia sin detenerlo correctamente. Verificar que `shutdown` detiene el `BackgroundScheduler` correctamente.
- Que el `contexto` no se reinicie entre parcelas, arrastrando datos de una parcela a la siguiente. `contexto = {}` debe inicializarse por parcela, no una sola vez por ciclo global.

### Criterio de finalización
Un ciclo completo, disparado manualmente en un test, actualiza correctamente estado, historial, eventos y alertas para múltiples parcelas, y un fallo aislado de Open-Meteo no detiene el resto. No se continúa a la Fase 15 si el ciclo no es resiliente a fallos de una parcela individual.

---

## Fase 15 — Endpoints internos restantes

### Objetivo
Exponer por HTTP los endpoints de uso interno del panel: lecturas, eventos manuales y control del controlador, más el endpoint de estado del propio servicio.

### Dependencias
Fase 14 completa (scheduler generando datos reales), Fase 12 completa (servicio de eventos).

### Tareas
1. En `app/routers/lecturas.py`, implementar `GET /parcelas/{id}/lecturas`, devolviendo el historial desde `LecturaSensorSimulada`, con la forma de respuesta del Blueprint (sección 9).
2. En `app/routers/eventos.py`, implementar `POST /parcelas/{id}/eventos`, invocando la función de creación de `evento_service` (Fase 12), devolviendo `201`.
3. En `app/routers/controlador.py`, implementar `PATCH /parcelas/{id}/controlador`, actualizando únicamente el campo `estado` del `ControladorSimulado` correspondiente, devolviendo `200`.
4. En `app/routers/status.py`, implementar `GET /status`, devolviendo `scheduler_activo`, `ultima_ejecucion`, `proxima_ejecucion` y `parcelas_activas`, usando lo expuesto por `scheduler_service` (Fase 14).
5. Incluir los cuatro routers en `app/main.py`.
6. Probar manualmente los cuatro endpoints desde `/docs` contra datos generados por un ciclo real o simulado del scheduler.
7. Agregar tests de integración para los cuatro endpoints (pueden agregarse a `tests/test_parcelas.py`, `tests/test_estado.py` o a archivos nuevos si se prefiere, siempre dentro de la carpeta `tests/` ya definida en la Fase 2).
8. Hacer commit (`feat(routers): exponer endpoints internos de lecturas, eventos, controlador y status`).

### Archivos involucrados
- Modificar: `app/routers/lecturas.py`, `app/routers/eventos.py`, `app/routers/controlador.py`, `app/routers/status.py`, `app/main.py`.
- Modificar: archivos de test correspondientes dentro de `tests/`.

### Resultado esperado
Los siete endpoints del Blueprint (cuatro del contrato oficial más estos cuatro internos, según tabla de la sección 10) están expuestos y funcionando.

### Validaciones
- [ ] `GET /parcelas/{id}/lecturas` devuelve el historial correcto tras uno o más ciclos del scheduler.
- [ ] `POST /parcelas/{id}/eventos` crea correctamente un `EventoManualPendiente` y responde `201`.
- [ ] `PATCH /parcelas/{id}/controlador` cambia el estado sin afectar sensores ni configuración estructural.
- [ ] `GET /status` refleja correctamente si el scheduler está activo y la próxima ejecución estimada.

### Riesgos
- Que `GET /parcelas/{id}/lecturas` termine siendo consumido accidentalmente por lógica pensada para Croply. Este endpoint es exclusivamente para el panel interno (Blueprint, decisión cerrada en la Documentación Funcional).

### Criterio de finalización
Los cuatro endpoints internos están expuestos, probados y funcionando contra datos reales del scheduler. No se continúa a la Fase 16 si alguno de los siete endpoints totales no responde según la tabla de la sección 10 del Blueprint.

---

## Fase 16 — Frontend del simulador

### Objetivo
Reemplazar el `index.html` de marcador de posición por el panel funcional descrito en el Blueprint.

### Dependencias
Fase 15 completa (todos los endpoints HTTP disponibles).

### Tareas
1. Montar `app/static/` como archivos estáticos en `app/main.py` usando `StaticFiles` de FastAPI (Blueprint, sección 16).
2. Reemplazar `app/static/index.html` por el panel real, sin frameworks (Blueprint, sección 16): barra de estado global que consulta `GET /status` cada 60 segundos, tabla por parcela con los últimos valores obtenida de `GET /parcelas/{id}/estado` al cargar la página, botones de eventos manuales que llaman a `POST /parcelas/{id}/eventos`, un log en memoria en JavaScript de las acciones realizadas, e historial expandible por sensor usando `GET /parcelas/{id}/lecturas?limit=50`.
3. Confirmar que la tabla de valores no hace polling automático de los datos de sensores (solo el estado global cada 60s), ya que los valores solo cambian cada 25 minutos (Blueprint, sección 16).
4. Probar manualmente el panel completo en el navegador contra datos reales generados por el scheduler: carga inicial, actualización de estado global, disparo de un evento manual, expansión de historial.
5. Hacer commit (`feat(frontend): implementar panel HTML funcional del simulador`).

### Archivos involucrados
- Modificar: `app/static/index.html`, `app/main.py`.

### Resultado esperado
El panel HTML funciona de punta a punta en el navegador, consumiendo únicamente los endpoints ya implementados, sin frameworks ni dependencias adicionales.

### Validaciones
- [ ] El panel carga correctamente en el navegador accediendo a la ruta estática servida por FastAPI.
- [ ] La tabla de parcelas muestra los últimos valores reales tras al menos un ciclo del scheduler.
- [ ] Un evento manual disparado desde un botón del panel efectivamente crea el `EventoManualPendiente` correspondiente (verificar en la base de datos o esperando el próximo ciclo).
- [ ] El historial expandible muestra las últimas lecturas de un sensor.

### Riesgos
- Agregar un framework frontend (React, Vue, etc.) por comodidad. El Blueprint es explícito: HTML/CSS/JS puro, sin frameworks (sección 16 de la Documentación Funcional, decisión cerrada).
- Hacer polling frecuente de los datos de sensores, generando carga innecesaria sin ningún beneficio, dado que los valores solo cambian cada 25 minutos.

### Criterio de finalización
El panel funciona completamente en el navegador contra datos reales, sin frameworks adicionales. No se continúa a la Fase 17 si el panel no refleja correctamente el estado real de al menos una parcela de prueba.

---

## Fase 17 — Docker y Docker Compose

### Objetivo
Que todo el stack (simulador + base de datos) levante con un solo comando, en un entorno local reproducible.

### Dependencias
Fase 16 completa (aplicación completa y funcional corriendo localmente sin Docker).

### Tareas
1. Crear el `Dockerfile` en la raíz del proyecto: imagen base Python acorde a la versión del Blueprint (sección 2), copia de `requirements.txt`, instalación de dependencias, copia del código de `app/`, comando de arranque con Uvicorn.
2. Crear `docker-compose.yml` en la raíz, replicando exactamente la configuración del Blueprint (sección 21): servicio `simulador` (build local, puerto `8000:8000`, variables de entorno `DATABASE_URL` y `SCHEDULER_INTERVAL_MINUTES`, `depends_on` con `condition: service_healthy`); servicio `db` con la imagen indicada en el Blueprint, variables `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB`, puerto `5432:5432`, `healthcheck` con `pg_isready`.
3. Verificar que `DATABASE_URL` del servicio `simulador` en `docker-compose.yml` apunta al host `db` (nombre del servicio), no a `localhost`.
4. Levantar únicamente la base de datos (`docker compose up -d db`) y confirmar que el `healthcheck` pasa.
5. Ejecutar las migraciones dentro de un contenedor efímero (`docker compose run --rm simulador alembic upgrade head`), exactamente como indica el Blueprint (sección 21).
6. Levantar el stack completo (`docker compose up`) y confirmar que el simulador arranca, se conecta a la base de datos y expone `/docs` en `localhost:8000`.
7. Confirmar que el scheduler arranca correctamente dentro del contenedor (revisar logs de arranque).
8. Hacer commit (`feat(docker): agregar Dockerfile y docker-compose para entorno local`).

### Archivos involucrados
- Crear: `Dockerfile`, `docker-compose.yml`.

### Resultado esperado
`docker compose up -d db`, luego `docker compose run --rm simulador alembic upgrade head`, y luego `docker compose up` dejan todo el sistema funcionando de punta a punta en local, sin pasos manuales adicionales.

### Validaciones
- [ ] `docker compose up -d db` deja el `healthcheck` de la base de datos en estado saludable.
- [ ] Las migraciones corren sin error dentro del contenedor efímero.
- [ ] `docker compose up` deja el simulador respondiendo en `http://localhost:8000/docs`.
- [ ] Los logs del contenedor `simulador` muestran el arranque del scheduler sin errores.
- [ ] Un ciclo completo del scheduler corre correctamente dentro del contenedor (esperar 25 minutos o disparar manualmente según el mecanismo de test de la Fase 14, si está expuesto también en este entorno).

### Riesgos
- Que el servicio `simulador` intente conectarse a la base de datos antes de que esté lista, a pesar del `depends_on`. El `healthcheck` con `condition: service_healthy` está para evitar justamente esto; no quitarlo.
- Usar `localhost` en vez del nombre del servicio `db` dentro de la red interna de Compose.

### Criterio de finalización
El stack completo levanta con los tres comandos indicados, sin pasos manuales adicionales ni errores en los logs. No se continúa a la Fase 18 si el `docker compose up` no dejó el sistema completamente funcional.

---

## Fase 18 — Pruebas finales y cierre

### Objetivo
Verificar que el proyecto completo funciona de punta a punta, está probado, y coincide exactamente con el Blueprint y la Documentación Funcional, antes de considerarlo terminado.

### Dependencias
Todas las fases anteriores completas.

### Tareas
1. Ejecutar la suite completa de tests (`pytest`) y confirmar que todos pasan, incluyendo los de sensores, servicios, routers y scheduler.
2. Recorrer manualmente el flujo funcional completo descrito en la Documentación Funcional (sección 7 — Flujo completo paso a paso): registrar una parcela, esperar o disparar un ciclo del scheduler, consultar `GET /parcelas/{id}/estado`, consultar el panel HTML, disparar un evento manual, reemplazar la configuración de la parcela con `PUT`, eliminar la parcela.
3. Revisar el árbol de archivos final contra el Blueprint (sección 4) y confirmar que no se agregó ningún archivo, carpeta o dependencia fuera de lo especificado.
4. Eliminar cualquier código muerto, comentario obsoleto, archivo de prueba temporal o `print()` de debugging que haya quedado de fases anteriores.
5. Confirmar que `requirements.txt` contiene exactamente las tecnologías y versiones del Blueprint (sección 2), sin librerías adicionales no utilizadas.
6. Confirmar que ningún endpoint, DTO o campo de la API difiere de lo documentado en el Blueprint (sección 9 y 10).
7. Confirmar que las decisiones pendientes del Blueprint (sección 23) siguen señaladas como tales en algún lugar visible del proyecto (por ejemplo, en el `README.md`), para que el equipo las revise antes de un eventual uso más allá de la demostración académica.
8. Escribir un `README.md` breve en la raíz con: cómo levantar el proyecto local (`.env`, `docker compose up`), cómo correr las migraciones, cómo correr los tests, y un enlace/mención a la Documentación Funcional y el Blueprint como fuentes de verdad del diseño.
9. Hacer commit final (`chore(cierre): limpieza final y verificación de consistencia con el Blueprint`).

### Archivos involucrados
- Puede modificarse cualquier archivo del proyecto únicamente para limpieza (eliminar código muerto), nunca para agregar funcionalidad nueva.
- Crear: `README.md`.

### Resultado esperado
El proyecto completo funciona de punta a punta, toda la suite de tests pasa, no queda código muerto ni desviaciones respecto al Blueprint, y existe un `README.md` que permite a cualquier persona levantar el entorno desde cero.

### Validaciones
- [ ] `pytest` corre sin fallos ni tests saltados sin justificación.
- [ ] El flujo funcional completo (alta → ciclo → estado → panel → evento → reemplazo → baja) se ejecuta sin errores de principio a fin.
- [ ] El árbol de archivos coincide con el Blueprint sin agregados no autorizados.
- [ ] `docker compose up` sigue funcionando tras la limpieza final.

### Riesgos
- Introducir una regresión durante la limpieza de código muerto. Volver a correr la suite completa de tests después de cualquier eliminación.
- Dar por “implícitamente resueltas” las decisiones pendientes del Blueprint (sección 23) sin que el equipo las haya confirmado realmente. Deben quedar documentadas como pendientes en el `README.md`, no ocultarse.

### Criterio de finalización
Todos los tests pasan, el flujo funcional completo se verificó manualmente, el árbol de archivos coincide con el Blueprint, y existe un `README.md` de arranque. Esta es la última fase: al cumplirse su criterio de finalización, el proyecto se considera implementado según el Blueprint y la Documentación Funcional vigentes.

---

*Plan de Implementación generado a partir de la Documentación Funcional y el Blueprint Técnico ya cerrados del proyecto. No repite su contenido; lo referencia por sección. Última actualización: julio 2026.*
