"""
Módulo principal de la aplicación web para monitoreo judicial.
Este archivo configura la aplicación FastAPI y define las rutas principales.
"""

from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import os
import logging
from pathlib import Path

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Monitor Judicial",
    description="Sistema de monitoreo y clasificación automatizada de procesos judiciales con IA generativa",
    version="0.1.0"
)

# Configurar directorio de plantillas y archivos estáticos
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "app", "static")), name="static")

# Importar módulos de la aplicación
from app.api.judicial_api import JudicialAPIClient
from app.services import get_ai_service
from app.models.database import get_db
from app.services.db_service import DatabaseService

# Crear instancia del cliente de la API
judicial_client = JudicialAPIClient()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal de la aplicación."""
    return templates.TemplateResponse("index.html", {"request": request, "title": "Monitor Judicial"})

@app.get("/buscar", response_class=HTMLResponse)
async def buscar_form(request: Request):
    """Formulario de búsqueda de procesos judiciales."""
    return templates.TemplateResponse("buscar.html", {"request": request, "title": "Buscar Procesos"})

@app.post("/buscar/razon-social")
async def buscar_razon_social(
    request: Request,
    nombre: str = Form(...),
    tipo_persona: str = Form("jur"),
    solo_activos: bool = Form(True),
    codificacion_despacho: str = Form(""),
    db: Session = Depends(get_db)
):
    """Busca procesos por razón social."""
    try:
        resultados = judicial_client.consultar_por_razon_social(
            nombre=nombre,
            tipo_persona=tipo_persona,
            solo_activos=solo_activos,
            codificacion_despacho=codificacion_despacho
        )
        
        # Guardar resultados en la base de datos
        if resultados.get('procesos'):
            for proceso in resultados['procesos']:
                datos_empresa = {
                    'nombre': nombre,
                    'tipo_persona': tipo_persona
                }
                DatabaseService.guardar_proceso(db, proceso, datos_empresa)
        
        return templates.TemplateResponse(
            "resultados.html", 
            {
                "request": request, 
                "title": f"Resultados para {nombre}",
                "resultados": resultados,
                "tipo_busqueda": "razon_social",
                "parametros": {
                    "nombre": nombre,
                    "tipo_persona": tipo_persona,
                    "solo_activos": solo_activos,
                    "codificacion_despacho": codificacion_despacho
                }
            }
        )
    except Exception as e:
        logger.error(f"Error en búsqueda por razón social: {str(e)}")
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request, 
                "title": "Error en la búsqueda",
                "error": str(e)
            }
        )

@app.post("/buscar/radicado")
async def buscar_radicado(
    request: Request,
    numero: str = Form(...),
    solo_activos: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Busca procesos por número de radicado."""
    try:
        resultados = judicial_client.consultar_por_radicado(
            numero=numero,
            solo_activos=solo_activos
        )
        
        # Guardar resultados en la base de datos
        if resultados.get('procesos'):
            for proceso in resultados['procesos']:
                DatabaseService.guardar_proceso(db, proceso)
        
        return templates.TemplateResponse(
            "resultados.html", 
            {
                "request": request, 
                "title": f"Resultados para radicado {numero}",
                "resultados": resultados,
                "tipo_busqueda": "radicado",
                "parametros": {
                    "numero": numero,
                    "solo_activos": solo_activos
                }
            }
        )
    except Exception as e:
        logger.error(f"Error en búsqueda por radicado: {str(e)}")
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request, 
                "title": "Error en la búsqueda",
                "error": str(e)
            }
        )

@app.get("/proceso/{id_proceso}")
async def detalle_proceso(request: Request, id_proceso: str, db: Session = Depends(get_db)):
    """Muestra el detalle de un proceso específico."""
    try:
        detalle = judicial_client.obtener_detalle_proceso(id_proceso)
        actuaciones = judicial_client.obtener_actuaciones_proceso(id_proceso)
        
        # Guardar detalles en la base de datos
        DatabaseService.guardar_detalle_proceso(db, id_proceso, detalle)
        
        # Guardar actuaciones en la base de datos
        if actuaciones.get('actuaciones'):
            DatabaseService.guardar_actuaciones(db, id_proceso, actuaciones['actuaciones'])
        
        # Generar resumen del proceso con IA
        ai_service = get_ai_service()
        resumen = ai_service.generar_resumen_proceso(
            detalle_proceso=detalle,
            actuaciones=actuaciones.get('actuaciones', [])
        )
        
        # Guardar resumen en la base de datos
        DatabaseService.guardar_resumen_proceso(db, id_proceso, resumen)
        
        # Clasificar actuaciones
        actuaciones_clasificadas = []
        if actuaciones.get('actuaciones'):
            for actuacion in actuaciones['actuaciones']:
                clasificacion = ai_service.clasificar_actuacion(actuacion)
                actuacion['clasificacion'] = clasificacion
                actuaciones_clasificadas.append(actuacion)
                
                # Guardar clasificación en la base de datos
                DatabaseService.guardar_clasificacion_actuacion(db, actuacion['idRegActuacion'], clasificacion)
        
        return templates.TemplateResponse(
            "detalle_proceso.html", 
            {
                "request": request, 
                "title": f"Proceso {detalle.get('llaveProceso', id_proceso)}",
                "detalle": detalle,
                "actuaciones": actuaciones,
                "resumen_ia": resumen,
                "actuaciones_clasificadas": actuaciones_clasificadas
            }
        )
    except Exception as e:
        logger.error(f"Error al obtener detalles del proceso: {str(e)}")
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request, 
                "title": "Error al obtener detalles",
                "error": str(e)
            }
        )

@app.get("/actuacion/{id_actuacion}")
async def detalle_actuacion(request: Request, id_actuacion: str, db: Session = Depends(get_db)):
    """Muestra el detalle de una actuación específica."""
    try:
        documentos = judicial_client.obtener_documentos_actuacion(id_actuacion)
        
        # Guardar documentos en la base de datos
        if documentos.get('documentos'):
            DatabaseService.guardar_documentos(db, id_actuacion, documentos['documentos'])
        
        return templates.TemplateResponse(
            "detalle_actuacion.html", 
            {
                "request": request, 
                "title": f"Actuación {id_actuacion}",
                "documentos": documentos
            }
        )
    except Exception as e:
        logger.error(f"Error al obtener documentos de la actuación: {str(e)}")
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request, 
                "title": "Error al obtener documentos",
                "error": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
