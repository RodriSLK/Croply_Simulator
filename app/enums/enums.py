from __future__ import annotations

from enum import Enum


class TipoSensorEnum(str, Enum):
    TEMP_HUME_AMBIENTAL = "TEMP_HUME_AMBIENTAL"
    HUMEDAD_SUELO = "HUMEDAD_SUELO"
    RADIACION_SOLAR = "RADIACION_SOLAR"
    PRECIPITACION = "PRECIPITACION"
    PH = "PH"


class EstadoTransmision(str, Enum):
    TRANSMITIENDO = "TRANSMITIENDO"
    SIN_SEÑAL = "SIN_SEÑAL"


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
