"""
Módulo para la integración de servicios de IA generativa en la aplicación.
Este archivo configura y proporciona acceso a los servicios de IA.
"""

import os
import logging
from app.services.ai_service import AIGenerativeService

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicializar el servicio de IA generativa
ai_service = AIGenerativeService(model_name="gpt-3.5-turbo")

def get_ai_service() -> AIGenerativeService:
    """
    Proporciona acceso al servicio de IA generativa.
    
    Returns:
        Instancia del servicio de IA generativa.
    """
    return ai_service
