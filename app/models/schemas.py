"""
Esquemas de datos para la aplicación de monitoreo judicial.
Define los modelos de datos utilizados para la validación y serialización.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProcesoBase(BaseModel):
    """Esquema base para un proceso judicial."""
    idProceso: str
    llaveProceso: Optional[str] = None
    fechaProceso: Optional[str] = None
    fechaUltimaActuacion: Optional[str] = None
    despacho: Optional[str] = None
    departamento: Optional[str] = None
    sujetosProcesales: Optional[str] = None
    esPrivado: Optional[bool] = False
    cantFilas: Optional[int] = 0

class ProcesoDetalle(ProcesoBase):
    """Esquema detallado de un proceso judicial."""
    fechaRadicacion: Optional[str] = None
    fechaRadicacionOriginal: Optional[str] = None
    claseProceso: Optional[str] = None
    tipoProceso: Optional[str] = None
    subTipoProceso: Optional[str] = None
    ubicacionExpediente: Optional[str] = None
    juez: Optional[str] = None
    ponente: Optional[str] = None
    demandantes: Optional[List[str]] = None
    demandados: Optional[List[str]] = None

class Actuacion(BaseModel):
    """Esquema para una actuación judicial."""
    idRegActuacion: str
    llaveProceso: Optional[str] = None
    consActuacion: Optional[int] = None
    fechaActuacion: Optional[str] = None
    actuacion: Optional[str] = None
    anotacion: Optional[str] = None
    fechaInicial: Optional[str] = None
    fechaFinal: Optional[str] = None
    fechaRegistro: Optional[str] = None
    codRegla: Optional[str] = None
    conDocumentos: Optional[bool] = False
    cant: Optional[int] = 0

class Documento(BaseModel):
    """Esquema para un documento judicial."""
    idRegDocumento: str
    idRegActuacion: str
    nombreDocumento: Optional[str] = None
    fechaDocumento: Optional[str] = None
    fechaPublicacion: Optional[str] = None
    urlDocumento: Optional[str] = None

class ConsultaRazonSocial(BaseModel):
    """Esquema para la consulta por razón social."""
    nombre: str
    tipo_persona: str = "jur"
    solo_activos: bool = True
    codificacion_despacho: str = ""
    pagina: int = 1

class ConsultaRadicado(BaseModel):
    """Esquema para la consulta por número de radicado."""
    numero: str
    solo_activos: bool = False
    pagina: int = 1

class ResumenProceso(BaseModel):
    """Esquema para el resumen de un proceso judicial."""
    id_proceso: str
    radicado: Optional[str] = None
    despacho: Optional[str] = None
    tipo: Optional[str] = None
    demandantes: Optional[str] = None
    demandados: Optional[str] = None
    fecha_ultima_actuacion: Optional[str] = None
    ultima_actuacion: Optional[str] = None
    estado_actual: Optional[str] = None
    resumen_generado: Optional[str] = None
    nivel_urgencia: Optional[str] = "Normal"
    fecha_consulta: datetime = Field(default_factory=datetime.now)

class ClasificacionActuacion(BaseModel):
    """Esquema para la clasificación de una actuación judicial."""
    id_actuacion: str
    tipo_actuacion: Optional[str] = None
    nivel_urgencia: str = "Normal"  # Urgente, Alta, Normal, Baja
    requiere_accion: bool = False
    fecha_limite: Optional[str] = None
    observaciones: Optional[str] = None
