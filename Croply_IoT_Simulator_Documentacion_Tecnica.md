# Croply IoT Simulator — Documentación Técnica Oficial

> **Versión:** 1.1 — revisión de consistencia  
> **Estado:** Diseño cerrado — listo para implementación  
> **Audiencia:** Equipo de desarrollo, colaboradores externos, modelos de IA  
> **Propósito:** Este documento es la referencia única y oficial del proyecto. Cualquier persona o IA que lo lea debe poder comprender completamente qué se va a construir, cómo funciona y cuáles son las decisiones que ya no deben volver a discutirse.

---

## Índice

1. [Contexto y problema](#1-contexto-y-problema)
2. [Visión general del sistema](#2-visión-general-del-sistema)
3. [Sistema 1 — Croply](#3-sistema-1--croply)
4. [Sistema 2 — Croply IoT Simulator](#4-sistema-2--croply-iot-simulator)
5. [Comunicación entre sistemas](#5-comunicación-entre-sistemas)
6. [Sincronización entre Croply y el Simulador](#6-sincronización-entre-croply-y-el-simulador)
7. [Flujo completo paso a paso](#7-flujo-completo-paso-a-paso)
8. [Modelos de datos](#8-modelos-de-datos)
9. [Scheduler de Croply](#9-scheduler-de-croply)
10. [API REST del simulador](#10-api-rest-del-simulador)
11. [Modelos de simulación por sensor](#11-modelos-de-simulación-por-sensor)
12. [Motor de eventos manuales](#12-motor-de-eventos-manuales)
13. [Frontend del simulador](#13-frontend-del-simulador)
14. [Tecnologías elegidas y justificación](#14-tecnologías-elegidas-y-justificación)
15. [Tecnologías descartadas y justificación](#15-tecnologías-descartadas-y-justificación)
16. [Estructura de carpetas del proyecto](#16-estructura-de-carpetas-del-proyecto)
17. [Decisiones cerradas — no reabrir](#17-decisiones-cerradas--no-reabrir)
18. [Pendientes y próximos pasos](#18-pendientes-y-próximos-pasos)

---

## 1. Contexto y problema

**Croply** es un sistema web de gestión agrícola orientado a pequeños y medianos productores. Uno de sus módulos centrales es el **Módulo de Monitoreo IoT**, cuya función es visualizar en tiempo real datos provenientes de sensores agrícolas instalados en las parcelas: temperatura, humedad del suelo, radiación solar, precipitación y pH.

**El problema:** el equipo de desarrollo no dispone de sensores físicos reales, ni del presupuesto para adquirirlos, ni de tierras donde instalarlos. Sin datos reales, el módulo IoT de Croply no puede funcionar ni demostrarse.

**La solución:** desarrollar un sistema independiente denominado **Croply IoT Simulator**, que genere datos sintéticos pero realistas para cada parcela registrada, basándose en datos climáticos reales obtenidos de una API meteorológica. Croply consume esos datos exactamente igual a como lo haría si consultara sensores físicos reales.

---

## 2. Visión general del sistema

El proyecto está compuesto por **dos sistemas completamente separados** que se comunican exclusivamente a través de una API REST. No comparten base de datos ni lógica de negocio.

```
┌─────────────────────────────────────────────────────────────┐
│                        CROPLY                               │
│   Sistema principal — dueño de toda la lógica de negocio   │
│   Backend: NestJS (Node.js)                                 │
│   Base de datos: propia (PostgreSQL)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │  API REST (HTTP)
                       │  POST   /parcelas        →  registra nueva parcela
                       │  PUT    /parcelas/{id}   →  actualiza configuración completa
                       │  DELETE /parcelas/{id}   →  elimina parcela y datos
                       │  GET    /parcelas/{id}/estado  ←  consulta estado actual (scheduler Croply)
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  CROPLY IoT SIMULATOR                       │
│   Servicio independiente — solo simula sensores             │
│   Backend: Python + FastAPI                                 │
│   Base de datos: propia (PostgreSQL)                         │
│   Scheduler: APScheduler (ciclo cada 25 minutos)            │
│   Fuente climática: Open-Meteo API                          │
└─────────────────────────────────────────────────────────────┘
```

**Principio fundamental:** para Croply, el simulador es transparente. Croply consulta una API y recibe valores de sensores. No sabe ni le importa si esos valores vienen de hardware físico o de una simulación. Cuando en el futuro existan sensores reales, solo cambia lo que hay detrás de la API; Croply no necesita ninguna modificación.

---

## 3. Sistema 1 — Croply

### 3.1. Rol

Croply es el **dueño de toda la información del dominio agrícola**. Administra el ABM completo de todas las entidades del negocio. El simulador no toma decisiones de negocio ni reemplaza a Croply en ningún aspecto.

### 3.2. Modelo de dominio relevante para el módulo IoT

Estas son las entidades de Croply que interactúan con el simulador:

#### Parcela
Representa una subdivisión de terreno dentro de una finca.

| Campo | Tipo | Descripción |
|---|---|---|
| idParcela | int | Identificador único |
| nombre | string | Nombre descriptivo |
| fechaAlta | datetime | Fecha de creación |
| fechaBaja | datetime | Fecha de baja (nullable) |
| estado | enum | ACTIVA / INACTIVA |

Una parcela tiene uno o varios `ControladorSensor`.

#### ControladorSensor
Representa un nodo físico (o simulado) instalado en la parcela. En el contexto del simulador, el controlador es un concepto lógico que agrupa sensores.

| Campo | Tipo | Descripción |
|---|---|---|
| idControladorSensor | int | Identificador único |
| ipControlador | string | IP del dispositivo (ficticia en simulación) |
| estadoControlador | enum | TRANSMITIENDO / SIN_SEÑAL |

Un controlador puede tener asociados varios `Sensor`.

#### Sensor
Representa un sensor individual. Los sensores **se crean dentro del controlador**, no tienen ABM independiente. Cada sensor queda vinculado a un `TipoSensor` al momento de su creación.

| Campo | Tipo | Descripción |
|---|---|---|
| id_Sensor | Long | Identificador único |
| fecha_Instalacion_Sensor | Date | Fecha de instalación del sensor |
| estado_senal | enum | TRANSMITIENDO / SIN_SEÑAL |
| ultimo_valor | Double | Última medición recibida |
| fecha_ultima_lectura | DateTime | Timestamp de esa última medición |
| ip_sensor | String | IP del sensor físico (ficticia en contexto de simulación) |

Cada sensor pertenece a un único `TipoSensor`.

> **Importante:** `ultimo_valor` y `fecha_ultima_lectura` en Croply se actualizan cuando Croply consulta la API del simulador y obtiene los nuevos valores. No los escribe el simulador directamente.

#### TipoSensor
Es un ABM independiente dentro de Croply, administrado en un apartado separado del sistema. Define los tipos de sensor disponibles. Al crear un sensor dentro de un controlador, el usuario selecciona qué `TipoSensor` le corresponde. Los tipos disponibles para esta versión son exactamente cinco:

| Código | Descripción |
|---|---|
| TEMP_HUME_AMBIENTAL | Temperatura y humedad ambiental (DHT22/SHT31) |
| HUMEDAD_SUELO | Humedad volumétrica del suelo — VWC |
| RADIACION_SOLAR | Radiación solar en W/m² |
| PRECIPITACION | Precipitación acumulada en mm |
| PH | pH del suelo |

#### LecturaSensor
Historial inmutable de todas las mediciones. Nunca se reemplazan lecturas anteriores.

| Campo | Tipo | Descripción |
|---|---|---|
| idLecturaSensor | int | Identificador único |
| valor | float | Valor medido |
| fechaHoraLectura | datetime | Timestamp exacto de la medición |

Relación de composición: `Sensor 1 ◆──── 0..* LecturaSensor`

### 3.3. Flujo de creación de una parcela en Croply

El flujo dentro de Croply antes de que el simulador entre en juego es el siguiente:

1. El usuario crea una **finca**.
2. El usuario crea una **parcela** dentro de esa finca.
3. Durante la creación de la parcela, también crea un **ControladorSensor**.
4. Dentro del controlador, el usuario **crea los sensores**. Cada sensor se crea en ese momento y se le vincula un `TipoSensor` (seleccionado del ABM independiente de tipos).
5. Lo normal es crear los cinco sensores (uno por cada tipo) dentro del controlador.
6. Una vez finalizada la creación, Croply conoce toda la configuración y **notifica al simulador** mediante `POST /parcelas`.

> **Distinción clave:** `TipoSensor` tiene ABM independiente en Croply (se gestiona en otro apartado del sistema). El `Sensor` en cambio **no** tiene ABM independiente: se crea directamente dentro del controlador y se le asigna un tipo en ese momento.

---

## 4. Sistema 2 — Croply IoT Simulator

### 4.1. Rol

El simulador tiene **una única responsabilidad:** generar lecturas sintéticas de sensores agrícolas para cada parcela registrada y exponerlas mediante una API REST.

**Lo que el simulador NO hace:**
- No administra lógica de negocio agrícola.
- No decide qué hacer con los datos (eso es Croply).
- No genera recomendaciones de riego ni alertas de negocio.
- No comparte base de datos con Croply.
- No escribe directamente en las entidades de Croply.

### 4.2. Cómo genera los datos

El simulador no genera números aleatorios. Basa la simulación en **datos climáticos reales** obtenidos de Open-Meteo para las coordenadas exactas de cada parcela, y aplica sobre esos datos modelos matemáticos y agronómicos documentados. Además añade ruido gaussiano a cada valor para emular la imperfección natural de un sensor físico real.

### 4.3. Ciclo de simulación

El scheduler se ejecuta cada **25 minutos**. En cada ciclo recorre todas las parcelas registradas y genera una lectura por sensor. Las lecturas **nunca se generan inmediatamente** después del `POST /parcelas`; siempre esperan al siguiente ciclo del scheduler.

```
Scheduler despierta (cada 25 min)
          │
          ▼
Obtiene todas las parcelas simuladas activas
          │
          ▼ (para cada parcela)
Consulta Open-Meteo con lat/lon de la parcela
          │
          ▼
Recibe: temperatura, humedad relativa,
        radiación solar, precipitación,
        nubosidad, viento
          │
          ▼
Aplica modelo matemático de cada sensor
          │
          ├─► Temperatura/Humedad → valor + VPD + ruido
          ├─► Radiación solar → W/m² + ETo + ruido
          ├─► Pluviómetro → mm + lluvia efectiva
          ├─► Humedad suelo → balance hídrico VWC (tiene estado)
          └─► pH → deriva lenta + variación diurna + ruido
          │
          ▼
Para cada SensorSimulado:
   1. Actualiza ultimoValor y fechaUltimaLectura en tabla sensores_simulados
   2. Inserta nueva fila en lecturas_simuladas (historial inmutable)
          │
          ▼
Evalúa motor de alertas internas (solo para monitoreo del simulador)
          │
          ▼
Ciclo completado — espera 25 minutos
```

### 4.4. Entidades internas del simulador

El simulador tiene su propia base de datos con entidades propias. Se llaman distinto que las de Croply para evitar confusión conceptual. **No son las mismas entidades**, son representaciones simplificadas que el simulador necesita para saber qué simular.

| Entidad en Croply | Entidad en Simulador |
|---|---|
| Parcela | ParcelaSimulada |
| ControladorSensor | ControladorSimulado |
| Sensor | SensorSimulado |
| LecturaSensor | LecturaSensorSimulada |

El simulador almacena únicamente los campos que necesita para ejecutar la simulación, no toda la información de negocio que maneja Croply.

---

## 5. Comunicación entre sistemas

### 5.1. Principio de desacoplamiento

Croply y el simulador **nunca comparten base de datos**. Toda comunicación es mediante HTTP sobre la API REST del simulador. Esto garantiza que ambos sistemas pueden evolucionar de forma independiente.

### 5.2. Dirección de la comunicación

```
Croply  ──POST /parcelas────►  Simulador   (registra nueva parcela)
Croply  ──PUT  /parcelas/{id}► Simulador   (actualiza configuración completa)
Croply  ──DELETE /parcelas/{id}►Simulador  (elimina parcela y su historial)
Croply  ◄──GET /parcelas/{id}/estado ────  Simulador  (consulta estado actual de sensores)
```

> **Croply nunca consulta el historial del simulador.** Cada sistema mantiene su propio historial de lecturas de forma completamente independiente. El simulador mantiene `LecturaSensorSimulada` para uso interno y del panel. Croply mantiene su propio `LecturaSensor` que construye a partir del estado actual que recibe del simulador.

### 5.3. El DTO como contrato de comunicación

Croply **no envía sus entidades internas** al simulador. En cambio, construye un **DTO (Data Transfer Object)** específicamente diseñado como contrato de comunicación entre ambos sistemas. Este DTO:

- Incluye únicamente la información que el simulador necesita para simular.
- Incluye `latitud` y `longitud` como parte de la parcela, aunque esos valores provengan de la entidad `Finca` en Croply. El simulador no necesita conocer la existencia de `Finca`.
- Usa los mismos IDs que Croply asignó a parcela, controlador y sensores.
- Traduce el `TipoSensor` (entidad ABM de Croply) a un código estable de texto (TEMP_HUME_AMBIENTAL, PH, etc.) que el simulador convierte a su enum interno.

### 5.4. Qué hace Croply con los datos que obtiene

El scheduler de Croply consulta `GET /parcelas/{id}/estado` al simulador cada 25 minutos:

1. Recibe el estado actual de cada sensor (`ultimoValor` y `fechaUltimaLectura` directamente de la entidad `SensorSimulado`).
2. **Actualiza** `ultimoValor` y `fechaUltimaLectura` en su entidad `Sensor`.
3. **Crea** una nueva fila en su propia `LecturaSensor` para mantener su historial independiente.
4. La interfaz de usuario de Croply consulta **únicamente la base de datos de Croply**. Nunca consulta al simulador directamente.

> El simulador no escribe en Croply. El simulador no expone su historial a Croply. Cada sistema es dueño de su propia historia de datos.

---

## 6. Sincronización entre Croply y el Simulador

Esta sección describe en detalle todos los escenarios de sincronización: creación, actualización, eliminación y manejo de errores.

### 6.1. Creación de una parcela — sincronización inicial

El flujo de sincronización se dispara automáticamente una vez que la transacción de creación de la parcela fue confirmada en la base de datos de Croply. No se sincroniza si la transacción falla.

```
[Transacción Croply confirmada]
         │
         ▼
Croply construye el DTO de la parcela
(incluye latitud/longitud de la Finca,
 controlador, sensores con tipo en código texto)
         │
         ▼
POST /parcelas  →  Simulador
         │
         ▼
Simulador responde 200 OK
         │
         ▼
Simulador almacena la configuración
usando exactamente los IDs recibidos de Croply
         │
         ▼
No genera lecturas inmediatamente.
Espera al siguiente ciclo del Scheduler (25 min).
```

### 6.2. Reintentos ante error de comunicación

Si el `POST /parcelas` falla (timeout, simulador apagado, error de red):

1. Croply registra el error internamente.
2. Croply reintenta automáticamente hasta **3 veces**.
3. Entre cada intento existe un **intervalo configurable**.
4. Si luego del tercer intento continúa fallando, Croply **notifica al usuario** que la sincronización no pudo completarse.

> No se utilizan colas de mensajes ni tecnologías como RabbitMQ o Kafka. Quedan fuera del alcance de esta versión. En futuras versiones podría incorporarse un mecanismo de sincronización más robusto.

### 6.3. Actualización de configuración de una parcela

Cada vez que ocurre un cambio estructural en una parcela de Croply (modificación de coordenadas, agregado o eliminación de un controlador, agregado, eliminación o modificación de un sensor), Croply reenvía **la configuración completa de la parcela** mediante:

```
PUT /parcelas/{id}
```

El simulador **toma esa nueva configuración como la configuración oficial vigente** y la reemplaza completamente. No necesita detectar qué cambió ni comparar con el estado anterior: no ejecuta ninguna lógica de diffing a nivel de aplicación. La implementación es un reemplazo íntegro: se eliminan los registros de `controladores_simulados` y `sensores_simulados` asociados a la parcela y se insertan nuevamente a partir del DTO recibido, conservando siempre los IDs enviados por Croply.

Como consecuencia natural de este reemplazo (no de una comparación explícita), el historial en `lecturas_simuladas` se ve afectado así:

- Si un sensor sigue formando parte de la nueva configuración, se reinserta con el mismo ID que ya tenía, por lo que sus lecturas anteriores permanecen asociadas sin cambios.
- Si un sensor deja de estar en la nueva configuración, su fila en `sensores_simulados` se elimina. La eliminación en cascada (definida a nivel de base de datos mediante la relación de composición `Sensor 1 ◆── 0..* LecturaSensorSimulada`) borra también sus lecturas históricas.

Una vez actualizada la configuración, el simulador espera al siguiente ciclo del Scheduler (25 minutos) para generar nuevas simulaciones. No ejecuta una simulación inmediatamente.

### 6.4. Eliminación de una parcela

Cuando una parcela es eliminada en Croply:

```
DELETE /parcelas/{id}
```

El simulador elimina en cascada:
- La `ParcelaSimulada`
- Sus `ControladorSimulado`
- Sus `SensorSimulado`
- Todas las `LecturaSensorSimulada` asociadas

A partir de ese momento deja de generar datos para esa parcela.

### 6.5. Conservación de IDs

El simulador **nunca genera identificadores propios** para parcelas, controladores ni sensores. Usa exactamente los IDs recibidos desde Croply. Esto simplifica la sincronización: siempre hay un único identificador compartido entre ambos sistemas para cada entidad.

### 6.6. TipoSensor — representación en cada sistema

`TipoSensor` existe de forma diferente en cada sistema, y es importante no confundirlos:

| Aspecto | En Croply | En el Simulador |
|---|---|---|
| Representación | Entidad con ABM propio (tabla en BD, CRUD completo) | Enum interno en Python |
| Administración | El equipo administra los tipos desde el backoffice de Croply | No tiene gestión propia; se define en código |
| Durante la comunicación | Envía el código estable en texto (TEMP_HUME_AMBIENTAL, PH, etc.) en el DTO | Recibe el código y lo convierte al enum para decidir qué algoritmo ejecutar |

> El enum del simulador es una **decisión interna de implementación** y no reemplaza ni duplica el ABM de `TipoSensor` en Croply. Son representaciones distintas del mismo concepto en cada contexto.

---

## 7. Flujo completo paso a paso

Este es el flujo de punta a punta desde que el usuario crea una parcela hasta que los datos aparecen en Croply:

```
[Usuario en Croply]
        │
        │  1. Crea finca (con latitud y longitud)
        │  2. Crea parcela dentro de la finca
        │  3. Crea controlador dentro de la parcela
        │  4. Crea sensores dentro del controlador
        │     (a cada sensor le vincula un TipoSensor del ABM)
        ▼
[Croply Backend - NestJS]
        │
        │  Transacción confirmada en BD de Croply
        │  Construye DTO incluyendo lat/lon de la Finca
        │  POST /parcelas  →  envía DTO al simulador
        │  Si falla: hasta 3 reintentos con intervalo configurable
        │  Si falla tras 3 intentos: notifica al usuario
        ▼
[Simulador - FastAPI]
        │
        │  Valida DTO
        │  Crea ParcelaSimulada (conserva ID de Croply)
        │  Crea ControladorSimulado (conserva ID de Croply)
        │  Crea SensorSimulado por cada sensor recibido
        │    → convierte código de tipo ("TEMP_HUME_AMBIENTAL") a enum interno
        │    → conserva ID de Croply para cada sensor
        │  Responde 200 OK
        │  No genera lecturas. Espera al próximo ciclo del Scheduler.
        ▼
[Hasta 25 minutos después — APScheduler]
        │
        │  Recorre todas las parcelas simuladas activas
        │  Para cada parcela:
        │    Obtiene lat/lon almacenados
        │    Consulta Open-Meteo con esas coordenadas
        │    Obtiene datos climáticos reales del momento
        │    Para cada SensorSimulado:
        │      Aplica algoritmo según tipo (enum interno)
        │      Actualiza ultimo_valor y fecha_ultima_lectura
        │      Inserta nueva LecturaSensorSimulada (historial)
        ▼
[Croply Backend — Scheduler de Croply (cada 25 min)]
        │
        │  GET /parcelas/{id}/estado
        │  Recibe estado actual de cada sensor
        │  (datos leídos de SensorSimulado, no del historial)
        │  Actualiza Sensor.ultimoValor en su BD
        │  Inserta LecturaSensor en su BD (historial propio)
        ▼
[Usuario en Croply]
        │
        │  La UI consulta únicamente la BD de Croply
        │  Ve los datos actualizados en el tablero de monitoreo IoT
        ▼
```

---

## 8. Modelos de datos

### 8.1. Base de datos del simulador

La base de datos del simulador es independiente de Croply. Utiliza **PostgreSQL**.

#### Tabla: `parcelas_simuladas`

| Campo | Tipo | Descripción |
|---|---|---|
| parcela_id | int (PK) | ID de la parcela en Croply |
| nombre | varchar | Nombre de la parcela |
| latitud | float | Coordenada de la finca |
| longitud | float | Coordenada de la finca |
| activa | boolean | Si debe simularse o no |
| creada_en | timestamp | Timestamp de registro |

> Las coordenadas corresponden a la **finca**, no a la parcela individual. Todas las parcelas de una misma finca comparten coordenadas para la consulta climática.

#### Tabla: `controladores_simulados`

| Campo | Tipo | Descripción |
|---|---|---|
| controlador_id | int (PK) | ID del controlador en Croply |
| parcela_id | int (FK) | Referencia a parcelas_simuladas |
| ip_controlador | varchar | IP ficticia (recibida de Croply, no se usa en simulación) |
| estado | varchar | `TRANSMITIENDO` / `SIN_SEÑAL` |

#### Tabla: `sensores_simulados`

| Campo | Tipo | Descripción |
|---|---|---|
| sensor_id | int (PK) | ID del sensor en Croply |
| controlador_id | int (FK) | Referencia a controladores_simulados |
| parcela_id | int (FK) | Desnormalizado para facilitar consultas por parcela sin joins adicionales |
| tipo | varchar | `TEMP_HUME_AMBIENTAL` / `HUMEDAD_SUELO` / `RADIACION_SOLAR` / `PRECIPITACION` / `PH` |
| ip_sensor | varchar | IP del sensor (recibida de Croply, no se usa en cálculos de simulación) |
| ultimo_valor | float | Último valor calculado por el scheduler |
| fecha_ultima_lectura | timestamp | Timestamp del último ciclo que calculó este sensor |

> **Campos internos adicionales para modelos con estado persistente:**
> - `vwc_actual` *(solo HUMEDAD_SUELO)*: estado del VWC que persiste entre ciclos. Es el único sensor cuyo valor depende del ciclo anterior.
> - `kc` *(solo HUMEDAD_SUELO)*: coeficiente de cultivo. Default 0.4 (suelo sin cultivo activo).
> - `profundidad_radicular` *(solo HUMEDAD_SUELO)*: en metros. Default 0.4.
> - `ph_base` *(solo PH)*: valor de pH inicial del suelo de esa parcela. Default 6.5.

#### Tabla: `lecturas_simuladas`

Tabla principal de historial. Se recomienda un índice compuesto sobre `(sensor_id, timestamp)` para optimizar las consultas por rango de fechas.

| Campo | Tipo | Descripción |
|---|---|---|
| id | bigint (PK) | Autoincremental |
| sensor_id | int (FK) | Referencia a sensores_simulados |
| parcela_id | int (FK) | Desnormalizado para facilitar consultas |
| tipo_sensor | varchar | Tipo del sensor (desnormalizado) |
| valor | float | Valor medido |
| unidad | varchar | `°C` / `%` / `W/m²` / `mm` / `pH` / `kPa` |
| timestamp | timestamp | Momento exacto de la medición |

> Una fila por sensor por ciclo. Cada ciclo de 25 minutos genera 5 filas por parcela (una por sensor).

#### Tabla: `alertas_simuladas` (interna — no expuesta a Croply)

**Finalidad:** esta tabla existe para que el equipo pueda verificar durante el desarrollo y la demo que los valores generados por el simulador son agronómicamente coherentes. Por ejemplo, si el VWC baja de 10% el simulador registra una alerta de `VWC_CRITICO`, lo que permite confirmar que el balance hídrico está funcionando correctamente. **Croply nunca consulta esta tabla.** No forma parte de la API pública del simulador. Es una herramienta de diagnóstico interno.

**Se persiste** en base de datos (no en memoria) para que el equipo pueda revisar el historial de alertas al inspeccionar la BD directamente o desde el panel HTML del simulador.

| Campo | Tipo | Descripción |
|---|---|---|
| id | int (PK) | Autoincremental |
| parcela_id | int (FK) | Parcela donde se detectó la condición |
| tipo | varchar | `HELADA` / `VWC_CRITICO` / `SATURACION` / `RIESGO_FUNGICO` / `ESTRES_HIDRICO` |
| valor_disparador | float | Valor exacto del sensor que activó la alerta |
| resuelta | boolean | `true` cuando la condición deja de cumplirse en un ciclo posterior |
| timestamp | timestamp | Momento en que se generó la alerta |

**Reglas que generan alertas:**

| Tipo | Condición |
|---|---|
| HELADA | Temperatura < 2°C |
| VWC_CRITICO | VWC < PMP + 20% del agua disponible |
| SATURACION | VWC > Capacidad de Campo |
| RIESGO_FUNGICO | HR > 80% con temperatura entre 15-25°C por 2+ ciclos consecutivos |
| ESTRES_HIDRICO | VPD > 1.8 kPa |

---

#### Tabla: `eventos_manuales_pendientes` (cola de un ciclo)

**Finalidad:** esta tabla funciona como una **cola de mensajes mínima** entre el panel HTML del simulador y el scheduler. Cuando el usuario presiona un botón en el panel (ej: "Riego", "Helada"), el endpoint `POST /parcelas/{id}/eventos` inserta una fila en esta tabla. En el próximo ciclo del scheduler, antes de calcular los valores de cada sensor, el scheduler consulta esta tabla buscando eventos pendientes para cada parcela, los aplica como modificadores sobre los datos de Open-Meteo, y los marca como `aplicado = true`. El ciclo siguiente ya no los encuentra y vuelve a la simulación normal.

**Se persiste** en base de datos para garantizar que el evento no se pierda si el scheduler está en medio de un ciclo cuando se dispara. También permite al panel mostrar el log de eventos históricos.

| Campo | Tipo | Descripción |
|---|---|---|
| id | int (PK) | Autoincremental |
| parcela_id | int (FK) | Parcela a la que afecta el evento |
| tipo_evento | varchar | `RIEGO` / `HELADA` / `LLUVIA` / `DERIVA_PH` / `DESCONECTAR_NODO` |
| parametros | jsonb | Parámetros variables por tipo (ej: `{"mm": 20}` para RIEGO, `{}` para HELADA) |
| aplicado | boolean | `false` hasta que el scheduler lo procesa; `true` después |
| creado_en | timestamp | Momento en que se disparó desde el panel |

> **Ciclo de vida de un evento:** el usuario presiona el botón → se inserta fila con `aplicado = false` → el scheduler lo detecta en su próximo ciclo → lo aplica durante ese ciclo → lo marca `aplicado = true` → el ciclo siguiente vuelve a la normalidad. Los eventos duran exactamente **un ciclo de 25 minutos**.

### 8.2. Diagrama de clases — Croply IoT Simulator

Diagrama UML de las entidades internas del simulador con sus atributos, relaciones y cardinalidades.

```
┌──────────────────────────────────┐
│         ParcelaSimulada          │
├──────────────────────────────────┤
│ + parcela_id: int (PK)           │
│ + nombre: varchar                │
│ + latitud: float                 │
│ + longitud: float                │
│ + activa: boolean                │
│ + creada_en: timestamp           │
└──────────────┬───────────────────┘
               │
               │ 1
               │
               │ tiene
               │
               │ 1
               ▼
┌──────────────────────────────────┐
│       ControladorSimulado        │
├──────────────────────────────────┤
│ + controlador_id: int (PK)       │
│ + parcela_id: int (FK)           │
│ + ip_controlador: varchar        │
│ + estado: EstadoTransmision      │
└──────────────┬───────────────────┘
               │
               │ 1
               │
               │ contiene
               │
               │ 1..*
               ▼
┌──────────────────────────────────┐
│          SensorSimulado          │
├──────────────────────────────────┤
│ + sensor_id: int (PK)            │
│ + controlador_id: int (FK)       │
│ + parcela_id: int (FK)           │
│ + tipo: TipoSensorEnum           │
│ + ip_sensor: varchar             │
│ + ultimo_valor: float            │
│ + fecha_ultima_lectura: timestamp│
│ ~ vwc_actual: float (*)          │
│ ~ kc: float (*)                  │
│ ~ profundidad_radicular: float (*│
│ ~ ph_base: float (**)            │
└──────────────┬───────────────────┘
               │
               │ 1
               │ ◆ composición
               │ genera
               │
               │ 0..*
               ▼
┌──────────────────────────────────┐
│       LecturaSensorSimulada      │
├──────────────────────────────────┤
│ + id: bigint (PK)                │
│ + sensor_id: int (FK)            │
│ + parcela_id: int (FK)           │
│ + tipo_sensor: varchar           │
│ + valor: float                   │
│ + unidad: varchar                │
│ + timestamp: timestamp           │
└──────────────────────────────────┘

(*) solo en sensores de tipo HUMEDAD_SUELO
(**) solo en sensores de tipo PH


──────────── Tablas auxiliares (sin relación directa de herencia) ────────────

┌──────────────────────────────────┐     ┌──────────────────────────────────┐
│         AlertaSimulada           │     │    EventoManualPendiente         │
├──────────────────────────────────┤     ├──────────────────────────────────┤
│ + id: int (PK)                   │     │ + id: int (PK)                   │
│ + parcela_id: int (FK)           │     │ + parcela_id: int (FK)           │
│ + tipo: TipoAlertaEnum           │     │ + tipo_evento: TipoEventoEnum    │
│ + valor_disparador: float        │     │ + parametros: jsonb              │
│ + resuelta: boolean              │     │ + aplicado: boolean              │
│ + timestamp: timestamp           │     │ + creado_en: timestamp           │
└──────────────────────────────────┘     └──────────────────────────────────┘
        │ FK → parcelas_simuladas                 │ FK → parcelas_simuladas
        └─────────────────────────────────────────┘


──────────── Enumeraciones ───────────────────────────────────────────────────

«enum»                    «enum»                    «enum»
EstadoTransmision         TipoSensorEnum            TipoAlertaEnum
─────────────────         ──────────────────        ──────────────────
TRANSMITIENDO             TEMP_HUME_AMBIENTAL       HELADA
SIN_SEÑAL                 HUMEDAD_SUELO             VWC_CRITICO
                          RADIACION_SOLAR           SATURACION
                          PRECIPITACION             RIESGO_FUNGICO
                          PH                        ESTRES_HIDRICO

«enum»
TipoEventoEnum
──────────────────
RIEGO
HELADA
LLUVIA
DERIVA_PH
DESCONECTAR_NODO
```

**Notas sobre el diagrama:**

- `ParcelaSimulada` y `ControladorSimulado` tienen relación **1 a 1**: en esta versión cada parcela tiene exactamente un controlador.
- `ControladorSimulado` y `SensorSimulado` tienen relación **1 a 1..\***: un controlador contiene uno o más sensores (normalmente cinco, uno por tipo).
- `SensorSimulado` y `LecturaSensorSimulada` tienen relación de **composición 1 a 0..\***: las lecturas no existen sin el sensor. Si el sensor se elimina, se eliminan sus lecturas.
- `AlertaSimulada` y `EventoManualPendiente` referencian `parcelas_simuladas` directamente vía FK. Son entidades auxiliares sin relación de composición fuerte.
- El campo `parcela_id` en `SensorSimulado` y `LecturaSensorSimulada` está **desnormalizado** intencionalmente para evitar joins innecesarios en las consultas más frecuentes (lecturas por parcela).

---

## 9. Scheduler de Croply

Croply posee su propio scheduler independiente, implementado en NestJS. Corre cada **25 minutos** y es el único mecanismo por el cual Croply obtiene datos del simulador.

### 9.1. Qué hace el scheduler de Croply

En cada ejecución:

1. Obtiene la lista de todas las parcelas activas registradas en Croply.
2. Para cada parcela, llama a `GET /parcelas/{id}/estado` en el simulador.
3. Recibe el estado actual de cada sensor (valores leídos de `SensorSimulado`, no del historial).
4. Actualiza `ultimoValor` y `fechaUltimaLectura` en la entidad `Sensor` de Croply.
5. Inserta una nueva fila en `LecturaSensor` de Croply para mantener su historial propio.

Este proceso ocurre aunque ningún usuario esté usando el sistema en ese momento.

### 9.2. Independencia de los dos schedulers

| Aspecto | Scheduler del Simulador | Scheduler de Croply |
|---|---|---|
| Tecnología | APScheduler (Python) | NestJS (Node.js) |
| Frecuencia | Cada 25 minutos | Cada 25 minutos |
| Qué hace | Consulta Open-Meteo, calcula valores, actualiza SensorSimulado, genera LecturaSensorSimulada | Consulta GET /parcelas/{id}/estado, actualiza Sensor, genera LecturaSensor propia |
| Fuente de datos | Open-Meteo API | API REST del simulador |
| Historial que genera | LecturaSensorSimulada (interno al simulador) | LecturaSensor (en BD de Croply) |

> Ambos schedulers son completamente independientes. Si el scheduler de Croply falla, el simulador sigue generando datos. Si el simulador se reinicia, el historial ya acumulado en Croply no se pierde.

### 9.3. La interfaz de usuario nunca consulta al simulador

La UI de Croply consulta **únicamente la base de datos de Croply**. Los datos que ve el usuario agricultor provienen del scheduler de Croply que los sincronizó previamente. En ningún momento el frontend de Croply hace llamadas directas al simulador.

---

## 10. API REST del simulador

El simulador expone una API REST construida con **FastAPI**. Todos los endpoints devuelven JSON. No hay autenticación en esta versión (herramienta interna de desarrollo).

### 10.1. Endpoints disponibles

#### `POST /parcelas`
Registra una nueva parcela simulada con su controlador y sensores. Operación **atómica**: si cualquier parte falla, nada se persiste. El simulador no comienza a generar datos inmediatamente; espera al próximo ciclo del scheduler.

**Body:**
```json
{
  "parcela": {
    "id": 1,
    "nombre": "Parcela Norte",
    "latitud": -32.89,
    "longitud": -68.84,
    "controlador": {
      "id": 3,
      "ip": "192.168.0.10",
      "estado": "TRANSMITIENDO",
      "sensores": [
        { "id": 10, "tipo": "TEMP_HUME_AMBIENTAL", "ip_sensor": "192.168.0.21" },
        { "id": 11, "tipo": "HUMEDAD_SUELO", "ip_sensor": "192.168.0.22" },
        { "id": 12, "tipo": "RADIACION_SOLAR", "ip_sensor": "192.168.0.23" },
        { "id": 13, "tipo": "PRECIPITACION", "ip_sensor": "192.168.0.24" },
        { "id": 14, "tipo": "PH", "ip_sensor": "192.168.0.25" }
      ]
    }
  }
}
```

> Los sensores se envían con su `id` (asignado por Croply al crearlos dentro del controlador), su `tipo` (derivado del `TipoSensor` vinculado) y su `ip_sensor`. El simulador almacena estos datos pero no usa `ip_sensor` en ningún cálculo.

**Por qué un único POST y no varios:** si se usaran endpoints separados (`POST /parcelas`, `POST /controladores`, `POST /sensores`), un fallo parcial dejaría al simulador en estado inconsistente (parcela sin sensores = incapaz de simular). La operación atómica garantiza que o todo queda registrado o nada queda registrado.

---

#### `PUT /parcelas/{id}`
Reenvía la configuración completa de una parcela existente. Este endpoint es el único mecanismo de actualización de configuración: Croply lo llama ante cualquier cambio estructural (modificación de coordenadas, cambios en controladores o sensores).

El simulador **reemplaza completamente** la configuración vigente con la nueva recibida. No compara ni detecta diferencias a nivel de aplicación: elimina y reinserta los registros de configuración a partir del DTO recibido, conservando los IDs enviados por Croply. Como consecuencia de este reemplazo, los sensores que continúan en la nueva configuración conservan su historial (mismo ID), mientras que los que ya no están presentes pierden su historial por eliminación en cascada a nivel de base de datos. Ver detalle en sección 6.3.

> **No existen endpoints individuales para controladores ni sensores.** Toda modificación de configuración se realiza siempre reenviando la parcela completa vía `PUT /parcelas/{id}`.

---

#### `DELETE /parcelas/{id}`
Elimina la parcela simulada y todos sus datos en cascada: controladores, sensores y lecturas históricas asociadas. A partir de ese momento el scheduler deja de generar datos para esa parcela.

---

#### `PATCH /parcelas/{id}/controlador`
Endpoint de uso exclusivo del **tablero de control** del simulador para el caso de uso "Desconectar nodo". Cambia el estado del controlador a `SIN_SEÑAL` o `TRANSMITIENDO` sin afectar la configuración estructural de la parcela.

> Este endpoint no es llamado por Croply. Es interno al simulador.

---

#### `POST /parcelas/{id}/eventos`
Inyecta un evento manual desde el tablero de control. El evento se persiste en `eventos_manuales_pendientes` y se aplica en el próximo ciclo del scheduler. Dura exactamente un ciclo y luego el sistema vuelve a la normalidad.

**Body:**
```json
{
  "tipo": "RIEGO",
  "parametros": {
    "mm": 20
  }
}
```

**Tipos de evento disponibles:**

| Tipo | Parámetros | Efecto en la simulación |
|---|---|---|
| `RIEGO` | `mm`: cantidad de agua en mm | Suma mm al balance hídrico. El VWC sube abruptamente. |
| `HELADA` | ninguno | Ignora Open-Meteo y fuerza temperatura descendente a -2°C por ciclo. |
| `LLUVIA` | `mm`: cantidad en mm | Inyecta precipitación intensa. VWC sube hasta posible saturación. |
| `DERIVA_PH` | ninguno | Comportamiento automático — el pH baja -0.001 por día (no necesita botón, es observable). |
| `DESCONECTAR_NODO` | ninguno | Llama a `PATCH /parcelas/{id}/controlador` con estado `SIN_SEÑAL`. El simulador deja de generar lecturas para esa parcela. |

---

#### `GET /parcelas/{id}/estado`
Devuelve el estado actual de todos los sensores de la parcela. **Este es el único endpoint que Croply consume** para obtener datos del simulador. Es invocado por el scheduler de Croply cada 25 minutos, no por la interfaz de usuario.

La información se obtiene directamente de la entidad `SensorSimulado` (campos `ultimo_valor` y `fecha_ultima_lectura`). **No consulta el historial** (`lecturas_simuladas`). No reconstruye valores: devuelve el último estado persistido.

**Response:**
```json
{
  "parcela_id": 1,
  "nombre": "Parcela Norte",
  "timestamp_simulacion": "2026-05-01T15:30:00Z",
  "controladores": [
    {
      "controlador_id": 3,
      "sensores": [
        { "sensor_id": 10, "tipo": "TEMP_HUME_AMBIENTAL", "valor_actual": 23.4, "unidad": "°C", "fecha_ultima_lectura": "2026-05-01T15:30:00Z" },
        { "sensor_id": 11, "tipo": "HUMEDAD_SUELO", "valor_actual": 31.2, "unidad": "%", "fecha_ultima_lectura": "2026-05-01T15:30:00Z" },
        { "sensor_id": 12, "tipo": "RADIACION_SOLAR", "valor_actual": 420.0, "unidad": "W/m²", "fecha_ultima_lectura": "2026-05-01T15:30:00Z" },
        { "sensor_id": 13, "tipo": "PRECIPITACION", "valor_actual": 0.0, "unidad": "mm", "fecha_ultima_lectura": "2026-05-01T15:30:00Z" },
        { "sensor_id": 14, "tipo": "PH", "valor_actual": 6.49, "unidad": "pH", "fecha_ultima_lectura": "2026-05-01T15:30:00Z" }
      ]
    }
  ]
}
```

---

#### `GET /parcelas/{id}/lecturas`
Devuelve el historial de lecturas del simulador. **Este endpoint es de uso exclusivo del panel HTML interno del simulador.** Croply no lo consume. Permite al equipo ver la evolución histórica de los valores en el tablero de control.

**Query params opcionales:** `?sensor_tipo=TEMP_HUME_AMBIENTAL&desde=2026-05-01&hasta=2026-05-02`

---

#### `GET /status`
Devuelve el estado actual del scheduler. Usado por el frontend del simulador para mostrar si el sistema está activo.

**Response:**
```json
{
  "scheduler_activo": true,
  "ultima_ejecucion": "2026-05-01T15:30:00Z",
  "proxima_ejecucion": "2026-05-01T15:55:00Z",
  "parcelas_activas": 3
}
```

---

## 11. Modelos de simulación por sensor

Cada sensor tiene su propio módulo Python con lógica de cálculo independiente. Todos reciben como entrada los datos climáticos de Open-Meteo y aplican ruido gaussiano al resultado final.

### Variables que provee Open-Meteo

Open-Meteo es consultada con las coordenadas de cada parcela. Variables consumidas:

| Variable Open-Meteo | Descripción | Sensor que la usa |
|---|---|---|
| `temperature_2m` | Temperatura del aire en °C | TEMP_HUME_AMBIENTAL, ETo |
| `relative_humidity_2m` | Humedad relativa en % | TEMP_HUME_AMBIENTAL, VPD |
| `shortwave_radiation` | Radiación solar en W/m² | RADIACION_SOLAR, ETo |
| `precipitation` | Precipitación en mm/h | PRECIPITACION, VWC |
| `cloud_cover` | Nubosidad en % | RADIACION_SOLAR |
| `wind_speed_10m` | Velocidad del viento en km/h | ETo |

> **Por qué Open-Meteo y no OpenWeather:** Open-Meteo es gratuita, no requiere API key y no tiene límite de llamadas. OpenWeather en tier gratuito tiene restricciones que con múltiples parcelas consultando cada 25 minutos podrían alcanzarse. Esta decisión está cerrada.

---

### Sensor TEMP_HUME_AMBIENTAL

**Módulo:** `sensores/temp_hume_ambiental.py`

**Entrada:** `temperature_2m`, `relative_humidity_2m`

**Proceso:**
- Aplica ruido gaussiano: ±0.3°C en temperatura, ±2% en humedad relativa.
- Calcula VPD (Déficit de Presión de Vapor) como variable derivada de alto valor agronómico.
- Puede tener un offset de microclima por parcela (ej: parcela con cobertura vegetal densa es 1-2°C más fresca).

**Fórmulas:**
```
Psat = 0.6108 × exp(17.27 × T / (T + 237.3))   [kPa]
VPD  = Psat × (1 - HR/100)                       [kPa]
```

**Valores de referencia:**

| VPD | Estado |
|---|---|
| < 0.4 kPa | Riesgo fúngico alto |
| 0.8 – 1.2 kPa | Óptimo |
| > 1.8 kPa | Estrés hídrico |

---

### Sensor RADIACION_SOLAR

**Módulo:** `sensores/radiacion_solar.py`

**Entrada:** `shortwave_radiation`, `cloud_cover`

**Proceso:**
- Aplica factor de nubosidad y ruido gaussiano ±5%.
- Integra la radiación horaria para obtener Rs en MJ/m²/día.
- Calcula ETo mediante Hargreaves-Samani. Esa ETo alimenta el cálculo del VWC.

**Fórmula ETo (Hargreaves-Samani):**
```
ETo (mm/día) = 0.0135 × (T_media + 17.8) × sqrt(Rs_MJ)
```

---

### Sensor PRECIPITACION

**Módulo:** `sensores/precipitacion.py`

**Entrada:** `precipitation` (mm/h de Open-Meteo)

**Proceso:**
- Convierte mm/h al formato de un pluviómetro tipping bucket.
- Resolución simulada: 0.2 mm por pulso.
- Calcula lluvia efectiva (umbral: más de 3 mm). Solo la lluvia efectiva impacta en el VWC.

**Fórmula lluvia efectiva:**
```
lluvia_efectiva = max(0, mm_evento - 3)
```

---

### Sensor HUMEDAD_SUELO (VWC)

**Módulo:** `sensores/humedad_suelo.py`

**Este es el sensor más complejo.** No viene directamente de Open-Meteo. Se calcula mediante balance hídrico usando la ETo del sensor de radiación y la lluvia efectiva del pluviómetro. Su estado persiste en la base de datos entre ciclos.

**Fórmula del balance hídrico:**
```
VWC(t+1) = VWC(t) - (ETo × Kc) / (Pf × Z) + lluvia_efectiva / (Pf × Z × 10)
```

**Parámetros por parcela:**

| Parámetro | Descripción | Valor por defecto |
|---|---|---|
| Kc | Coeficiente de cultivo | 0.4 (suelo sin cultivo) |
| Pf | Porosidad del suelo | 0.45 (franco) |
| Z | Profundidad radicular (m) | 0.4 |

**Rangos de referencia:**

| VWC | Estado agronómico |
|---|---|
| < 10% | Crítico — daño celular |
| 10 – 15% | Marchitez permanente |
| 15 – 25% | Estrés leve |
| 25 – 60% | Zona óptima |
| > 60% | Saturación — anoxia radicular |

> Este sensor es el que genera variación realista entre parcelas: ante el mismo clima, dos parcelas con distinto tipo de suelo o cultivo activo responden diferente.

---

### Sensor PH

**Módulo:** `sensores/ph.py`

**Entrada:** no depende del clima en el corto plazo.

**Proceso:**
- Parte de un `ph_base` configurado por parcela (default 6.5).
- Aplica deriva lenta de acidificación.
- Aplica variación diurna (fotosíntesis de día sube pH, respiración de noche lo baja).
- Aplica ruido gaussiano pequeño.

**Fórmula:**
```
pH(t) = ph_base + drift_acumulado + variacion_diurna + ruido(σ=0.02)

drift:            -0.001 a -0.005 pH/día
variacion_diurna: ±0.1 × sin(2π × hora / 24)
```

---

## 12. Motor de eventos manuales

El scheduler, antes de calcular los valores de cada sensor, verifica si existen eventos manuales pendientes para esa parcela en la tabla `eventos_manuales_pendientes`. Si existe alguno, lo aplica durante ese ciclo y lo marca como `aplicado = true`. El ciclo siguiente vuelve a la normalidad.

### Comportamiento por tipo de evento

**RIEGO:**
- Suma los mm indicados directamente al balance hídrico del VWC antes del cálculo normal.
- El VWC sube abruptamente en ese ciclo.
- Desde el frontend: el usuario ingresa cantidad en mm y presiona el botón.

**HELADA:**
- El scheduler ignora la temperatura de Open-Meteo para esa parcela.
- Fuerza la temperatura a descender progresivamente hasta valores negativos.
- Dispara alerta interna de helada.

**LLUVIA:**
- Inyecta precipitación intensa (mm indicados).
- El pluviómetro registra el evento y el VWC puede alcanzar saturación.

**DERIVA_PH:**
- Es automática. El pH ya deriva naturalmente -0.001 por día en el modelo.
- No tiene botón en el tablero; se observa en el historial a lo largo del tiempo.

**DESCONECTAR_NODO:**
- Llama internamente a `PATCH /parcelas/{id}/controlador` con `estado = SIN_SEÑAL`.
- El scheduler omite esa parcela en los ciclos siguientes hasta que se reconecte.
- El frontend muestra el sensor como "fuera de línea".

---

## 13. Frontend del simulador

### 13.1. Propósito

El frontend es una herramienta **interna de desarrollo y demostración**. Solo la usa el equipo para verificar que el simulador funciona correctamente y para mostrar el funcionamiento en la presentación final. No es parte de Croply y no la ve el usuario agricultor.

### 13.2. Stack

HTML + CSS + JavaScript puro servido directamente por FastAPI desde el mismo proceso. **Sin React, sin Vue, sin frameworks adicionales.** Una sola página, un solo archivo HTML con `fetch` nativo para consumir la API del simulador.

### 13.3. Estructura de la página

```
┌─────────────────────────────────────────────────────┐
│  Croply IoT Simulator                  ● Activo     │
│  Último ciclo: 15:30  |  Próximo: 15:55  |  3 parc.│
└─────────────────────────────────────────────────────┘

┌─ Parcela Norte (id: 1) ────────────────────────────┐
│                                                     │
│  Sensor           Valor      Unidad   Timestamp     │
│  TEMP_HUME_AMBIENTAL  23.4       °C       15:30:01      │
│  HUMEDAD_SUELO    31.2       %        15:30:01      │
│  RADIACION_SOLAR      420.0      W/m²     15:30:01      │
│  PRECIPITACION        0.0        mm       15:30:01      │
│  PH               6.49       pH       15:30:01      │
│                                                     │
│  [Riego]  [Helada]  [Lluvia]  [Desconectar nodo]    │
│                                                     │
│  Log de eventos:                                    │
│  15:28 — Helada forzada activada                    │
│  15:00 — Riego manual (20mm) activado               │
│                                                     │
│  [Ver historial ▼]                                  │
└─────────────────────────────────────────────────────┘

┌─ Parcela Sur (id: 2) ──────────────────────────────┐
│  ... (mismo bloque) ...                             │
└─────────────────────────────────────────────────────┘
```

### 13.4. Comportamiento de la tabla principal

- Muestra el **estado actual** de cada sensor: el `ultimo_valor` de cada `SensorSimulado`.
- Se actualiza cada vez que el scheduler corre (cada 25 minutos), no con polling frecuente.
- La página puede recargarse manualmente o hacer fetch al `GET /parcelas/{id}/estado` al cargar.
- No tiene sentido hacer polling frecuente porque los datos solo cambian cada 25 minutos.

### 13.5. Comportamiento del historial

- Se despliega al hacer click en "Ver historial".
- Consume `GET /parcelas/{id}/lecturas`.
- Muestra todas las lecturas anteriores ordenadas por timestamp descendente.
- Crece con cada ciclo del scheduler.

### 13.6. Comportamiento de los botones de eventos

- Al hacer click, el botón llama a `POST /parcelas/{id}/eventos`.
- Se deshabilita visualmente para ese ciclo para evitar doble disparo.
- El efecto es visible en la tabla principal en el siguiente ciclo (25 minutos).
- El log muestra los últimos eventos disparados con su timestamp.

### 13.7. Lo que el frontend NO incluye

- Login o autenticación.
- Gráficos complejos (pueden agregarse con Chart.js en versiones futuras si el tiempo lo permite).
- Configuración de parámetros internos del simulador (Kc, profundidad radicular, etc.).
- Nada relacionado con la lógica de negocio de Croply.

---

## 14. Tecnologías elegidas y justificación

| Tecnología | Rol | Justificación |
|---|---|---|
| **Python** | Lenguaje del simulador | Definido por el equipo. Ecosistema ideal para simulación científica y matemática. |
| **FastAPI** | Framework web / API REST | Moderno, rápido, documentación Swagger automática incluida. NestJS lo consume sin configuración especial. |
| **APScheduler** | Scheduler de ciclos | Librería Python simple para tareas recurrentes. El ciclo de 25 minutos se configura en pocas líneas. Sin complejidad extra. |
| **PostgreSQL** | Base de datos relacional | Conocida por el equipo. Robusta, SQL estándar. Suficiente para el volumen de datos del simulador (10-15 parcelas, 5 sensores cada una, un ciclo cada 25 minutos). |
| **Open-Meteo** | Fuente de datos climáticos | Gratuita, sin API key, sin límite de llamadas. Devuelve exactamente las variables necesarias para los modelos de sensores. |
| **Docker (básico)** | Contenedorización | Un único `docker-compose.yml` con dos servicios: simulador Python y PostgreSQL. Cualquier integrante del equipo levanta el sistema con un solo comando. |
| **Railway** | Plataforma de despliegue | Ya utilizada por el equipo para Croply. Soporta Docker y Python sin configuración compleja. |
| **HTML/CSS/JS puro** | Frontend del simulador | Sin frameworks adicionales. Liviano, sin dependencias, fácil de mantener. Servido por el mismo proceso FastAPI. |

---

## 15. Tecnologías descartadas y justificación

Estas tecnologías fueron evaluadas y descartadas. **No deben volver a proponerse** salvo que cambien fundamentalmente los requisitos del proyecto.

| Tecnología | Motivo del descarte |
|---|---|
| **MQTT / Eclipse Mosquitto** | MQTT tiene sentido cuando sensores físicos reales empujan datos de forma continua. En un simulador Python que corre de forma programada cada 25 minutos, agregar MQTT es complejidad sin beneficio real. Requiere aprender el protocolo, configurar broker, puertos, autenticación y QoS. |
| **Node-RED** | Motor de orquestación pensado para flujos de hardware IoT. No agrega valor en un simulador de software puro. Requiere aprender una herramienta adicional que el equipo no conoce. |
| **InfluxDB** | Base de datos especializada en series temporales con su propio query language (Flux). El volumen de datos del simulador (5 sensores × parcela cada 25 minutos) no justifica una base de datos adicional; PostgreSQL estándar, ya conocido por el equipo, es suficiente. |
| **RabbitMQ** | Broker de mensajería para arquitecturas de microservicios de alta escala. Totalmente innecesario para un simulador de 10-15 parcelas. |
| **OpenWeather API** | Tiene límites en tier gratuito (60 llamadas/minuto) que podrían alcanzarse con múltiples parcelas. Open-Meteo no tiene esa restricción. |
| **Web scraping climático** | Técnica frágil que se rompe si el sitio cambia su HTML. Va contra términos de uso de la mayoría de sitios. No se justifica cuando existen APIs gratuitas y sin límites disponibles. |
| **Grafana** | Herramienta de visualización poderosa pero que requiere levantar un servicio adicional en Docker. El panel HTML simple cumple el objetivo de demostración sin dependencias extra. |
| **React / Vue** | El frontend del simulador es una herramienta interna simple. Un framework frontend agrega tiempo de setup y complejidad innecesaria para una página de monitoreo básica. |

---

## 16. Estructura de carpetas del proyecto

```
croply-iot-simulator/
│
├── app/
│   ├── main.py                  # FastAPI app — endpoints + sirve frontend HTML
│   ├── scheduler.py             # APScheduler — ciclo cada 25 minutos
│   ├── sincronizacion.py        # Lógica de sync con Croply (POST/PUT/DELETE + reintentos)
│   ├── database.py              # Conexión a PostgreSQL y funciones CRUD
│   ├── openmeteo.py             # Cliente HTTP para Open-Meteo
│   ├── alertas.py               # Motor de reglas de alertas internas
│   │
│   ├── sensores/
│   │   ├── temp_hume_ambiental.py  # Modelo DHT22 — temperatura, HR, VPD
│   │   ├── radiacion_solar.py      # Piranómetro — W/m² y cálculo ETo
│   │   ├── precipitacion.py        # Tipping bucket — mm y lluvia efectiva
│   │   ├── humedad_suelo.py     # Balance hídrico VWC (tiene estado persistente)
│   │   └── ph.py                # Deriva lenta + variación diurna
│   │
│   ├── eventos/
│   │   └── procesador.py        # Aplica eventos manuales pendientes al ciclo
│   │
│   └── static/
│       └── index.html           # Frontend del simulador (HTML/CSS/JS puro)
│
├── docker-compose.yml           # Servicio simulador + PostgreSQL
├── Dockerfile
└── requirements.txt
```

---

## 17. Decisiones cerradas — no reabrir

Esta sección lista las decisiones de diseño que ya fueron tomadas y justificadas. No deben volver a discutirse salvo cambio fundamental de requisitos.

| # | Decisión | Razón |
|---|---|---|
| 1 | **Arquitectura de dos sistemas separados** | Croply y el simulador son independientes. Comunicación solo por API REST. Sin base de datos compartida. |
| 2 | **Open-Meteo como fuente climática** | Gratuita, sin key, sin límites. OpenWeather descartada. |
| 3 | **PostgreSQL estándar sobre InfluxDB** | El volumen de datos del simulador no justifica una base de datos especializada en series temporales. PostgreSQL, ya conocido por el equipo, es suficiente. |
| 4 | **Sin MQTT en esta versión** | Sin hardware físico real no hay justificación para el protocolo. Python escribe directo en BD. |
| 5 | **DTO atómico en POST /parcelas** | Un solo request con parcela + controlador + sensores evita estados inconsistentes. El DTO no expone entidades internas de Croply. |
| 6 | **Eventos manuales duran exactamente un ciclo** | Simplicidad. El scheduler los aplica, los marca como procesados y el siguiente ciclo vuelve a la normalidad. |
| 7 | **Coordenadas viajan en el DTO de la parcela, provienen de la Finca** | El simulador no conoce la entidad Finca. Croply incluye lat/lon en el DTO de la parcela aunque sean atributos de la Finca. |
| 8 | **`ip_controlador` e `ip_sensor` se reciben pero no se usan en cálculos** | Existen en el modelo de Croply. El simulador los almacena por fidelidad al contrato pero no los usa en la simulación. |
| 9 | **Exactamente 5 tipos de sensor por controlador** | Definido por el modelo de dominio de Croply. No cambia en esta versión. |
| 10 | **Frontend servido por FastAPI** | Sin servidor adicional. Una sola página HTML. Sin frameworks frontend. |
| 11 | **Tabla principal del simulador se actualiza cada 25 min** | Los datos solo cambian cuando corre el scheduler. Polling frecuente no agrega valor. |
| 12 | **El simulador no escribe en Croply y no expone su historial a Croply** | Croply solo consulta el estado actual vía GET /estado. Cada sistema mantiene su historial independiente. |
| 13 | **Nombres distintos para entidades del simulador** | `SensorSimulado`, `LecturaSensorSimulada`, etc. para evitar confusión con las entidades de Croply. |
| 14 | **El simulador conserva los IDs de Croply** | Parcela, controlador y sensores usan exactamente el mismo ID que Croply asignó. No se generan IDs propios. |
| 15 | **Actualización via PUT con reemplazo completo** | No existen endpoints individuales para controladores ni sensores. El PUT reemplaza toda la configuración sin detectar diferencias. |
| 16 | **Reintentos sin colas de mensajes** | Hasta 3 reintentos con intervalo configurable. Sin RabbitMQ, Kafka u otras tecnologías de mensajería. Fuera del alcance de esta versión. |
| 17 | **Ambos schedulers corren cada 25 minutos** | Simulador: genera datos desde Open-Meteo. Croply: sincroniza estado desde el simulador. Independientes entre sí. |
| 18 | **TipoSensor como enum en el simulador** | Decisión interna de implementación. No reemplaza el ABM de TipoSensor en Croply. Croply envía el código en texto; el simulador lo convierte a enum para elegir el algoritmo. |
| 19 | **Endpoint GET /parcelas/{id}/estado** | Único endpoint que Croply consume. Lee de SensorSimulado directamente, sin tocar lecturas_simuladas. No devuelve historial. |
| 20 | **Croply nunca consulta el historial del simulador** | GET /parcelas/{id}/lecturas es solo para el panel interno del simulador. Croply construye su propio historial a partir del estado actual que recibe. |
| 21 | **La UI de Croply solo consulta la BD de Croply** | En ningún momento el frontend de Croply llama directamente al simulador. Solo el scheduler de Croply interactúa con el simulador. |
| 22 | **Enums de TipoSensor definitivos** | `PH`, `RADIACION_SOLAR`, `HUMEDAD_SUELO`, `TEMP_HUME_AMBIENTAL`, `PRECIPITACION`. No usar otros valores en ningún lugar del sistema.

---

## 18. Pendientes y próximos pasos

### Lo que ya está definido y cerrado

El scheduler de Croply que consume `GET /parcelas/{id}/estado` cada 25 minutos está definido como decisión arquitectónica (ver sección 9). Su implementación es responsabilidad del equipo de Croply (NestJS), no del simulador.

### Coordinación pendiente con el equipo de Croply

- [ ] Confirmar el formato exacto del DTO del `POST /parcelas` y el `PUT /parcelas/{id}` — puede haber campos adicionales según la implementación de NestJS.
- [ ] Confirmar el formato de respuesta de `GET /parcelas/{id}/estado` que Croply espera recibir para actualizar sus entidades.

### Orden de implementación recomendado

1. `database.py` — conexión y creación de tablas en PostgreSQL.
2. `openmeteo.py` — cliente HTTP que dado lat/lon devuelve las variables climáticas actuales.
3. Módulos de sensores en orden: `temp_hume_ambiental.py` → `radiacion_solar.py` → `precipitacion.py` → `humedad_suelo.py` → `ph.py`.
4. `scheduler.py` — ciclo de 25 minutos que orquesta los pasos anteriores para cada parcela activa.
5. `sincronizacion.py` — lógica de recepción y actualización de configuración desde Croply (POST, PUT, DELETE con reintentos).
6. `main.py` — FastAPI con todos los endpoints definidos.
7. `eventos/procesador.py` — motor de eventos manuales integrado al scheduler.
8. `alertas.py` — motor de reglas internas.
9. `static/index.html` — frontend del simulador.
10. `Dockerfile` y `docker-compose.yml` — contenedorización y verificación local.
11. Despliegue en Railway y verificación de funcionamiento 24/7.

---

*Documento generado a partir de conversaciones de diseño del equipo. Última actualización: Julio 2026.*
