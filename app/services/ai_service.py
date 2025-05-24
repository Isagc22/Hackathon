"""
Servicio para la generación de resúmenes con IA generativa.
Este módulo proporciona funciones para resumir y clasificar actuaciones judiciales.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json

# Importar configuración
import app.config

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIGenerativeService:
    """Servicio para la generación de resúmenes y clasificación con IA generativa."""
    
    def __init__(self, model_name="gpt-3.5-turbo"):
        """
        Inicializa el servicio de IA generativa.
        
        Args:
            model_name: Nombre del modelo de lenguaje a utilizar.
        """
        # Configurar modelo de lenguaje
        self.model_name = model_name
        
        # Usar un enfoque de simulación para desarrollo sin API key real
        self.use_simulation = True
        
        if not self.use_simulation:
            self.chat_model = ChatOpenAI(
                model_name=model_name,
                temperature=0.3
            )
        
        logger.info(f"Servicio de IA generativa inicializado con modelo: {model_name}")
    
    def generar_resumen_proceso(self, detalle_proceso: Dict, actuaciones: List[Dict]) -> str:
        """
        Genera un resumen del proceso judicial basado en sus detalles y actuaciones.
        
        Args:
            detalle_proceso: Detalles del proceso judicial.
            actuaciones: Lista de actuaciones del proceso.
            
        Returns:
            Resumen generado del proceso.
        """
        # Si estamos en modo simulación, devolver un resumen predefinido
        if self.use_simulation:
            return self._generar_resumen_simulado(detalle_proceso, actuaciones)
        
        # Preparar el contexto para el modelo
        demandantes = ", ".join(detalle_proceso.get("demandantes", ["No especificado"]))
        demandados = ", ".join(detalle_proceso.get("demandados", ["No especificado"]))
        
        # Seleccionar las actuaciones más recientes (máximo 5)
        actuaciones_recientes = actuaciones[:5] if len(actuaciones) > 5 else actuaciones
        
        # Crear el texto de actuaciones
        texto_actuaciones = ""
        for i, act in enumerate(actuaciones_recientes):
            texto_actuaciones += f"{i+1}. Fecha: {act.get('fechaActuacion', 'No especificada')}\n"
            texto_actuaciones += f"   Actuación: {act.get('actuacion', 'No especificada')}\n"
            texto_actuaciones += f"   Anotación: {act.get('anotacion', 'No especificada')}\n\n"
        
        # Crear el prompt para el modelo
        system_prompt = """
        Eres un asistente legal especializado en procesos judiciales colombianos. 
        Tu tarea es generar un resumen conciso pero informativo de un proceso judicial 
        basado en sus detalles y actuaciones recientes.
        
        El resumen debe:
        1. Ser claro y directo, utilizando lenguaje profesional pero comprensible
        2. Identificar los aspectos más relevantes del proceso
        3. Destacar las actuaciones más importantes y su impacto en el proceso
        4. Tener una extensión de 3-5 párrafos
        5. Evitar tecnicismos excesivos o jerga legal innecesaria
        """
        
        human_prompt = f"""
        Detalles del proceso:
        - Radicado: {detalle_proceso.get('llaveProceso', 'No especificado')}
        - Fecha de radicación: {detalle_proceso.get('fechaRadicacion', 'No especificada')}
        - Despacho: {detalle_proceso.get('despacho', 'No especificado')}
        - Clase de proceso: {detalle_proceso.get('claseProceso', 'No especificada')}
        - Tipo de proceso: {detalle_proceso.get('tipoProceso', 'No especificado')}
        - Demandantes: {demandantes}
        - Demandados: {demandados}
        
        Actuaciones recientes:
        {texto_actuaciones}
        
        Por favor, genera un resumen conciso pero informativo del proceso judicial.
        """
        
        try:
            # Generar el resumen
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.chat_model.invoke(messages)
            resumen = response.content
            
            logger.info(f"Resumen generado para el proceso {detalle_proceso.get('llaveProceso', 'desconocido')}")
            return resumen
        
        except Exception as e:
            logger.error(f"Error al generar resumen: {str(e)}")
            return "No se pudo generar un resumen automático para este proceso."
    
    def clasificar_actuacion(self, actuacion: Dict) -> Dict:
        """
        Clasifica una actuación judicial según su urgencia y tipo.
        
        Args:
            actuacion: Datos de la actuación judicial.
            
        Returns:
            Diccionario con la clasificación de la actuación.
        """
        # Si estamos en modo simulación, devolver una clasificación predefinida
        if self.use_simulation:
            return self._clasificar_actuacion_simulada(actuacion)
        
        # Preparar el contexto para el modelo
        texto_actuacion = actuacion.get('actuacion', '')
        texto_anotacion = actuacion.get('anotacion', '')
        fecha_actuacion = actuacion.get('fechaActuacion', '')
        
        # Crear el prompt para el modelo
        system_prompt = """
        Eres un asistente legal especializado en procesos judiciales colombianos.
        Tu tarea es clasificar una actuación judicial según su urgencia y tipo.
        
        Debes proporcionar:
        1. Nivel de urgencia: "Urgente", "Alta", "Normal" o "Baja"
        2. Tipo de actuación: Categoría general (ej. "Audiencia", "Requerimiento", "Notificación", etc.)
        3. Si requiere acción inmediata: true o false
        4. Una breve justificación de la clasificación (1-2 oraciones)
        
        Responde en formato JSON con las siguientes claves:
        {
            "nivel_urgencia": "Urgente|Alta|Normal|Baja",
            "tipo_actuacion": "string",
            "requiere_accion": boolean,
            "justificacion": "string"
        }
        """
        
        human_prompt = f"""
        Actuación judicial:
        - Fecha: {fecha_actuacion}
        - Actuación: {texto_actuacion}
        - Anotación: {texto_anotacion}
        
        Clasifica esta actuación según su urgencia y tipo.
        """
        
        try:
            # Generar la clasificación
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.chat_model.invoke(messages)
            clasificacion_texto = response.content
            
            # Extraer el JSON de la respuesta
            try:
                # Intentar encontrar el JSON en la respuesta
                json_start = clasificacion_texto.find('{')
                json_end = clasificacion_texto.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    clasificacion_json = json.loads(clasificacion_texto[json_start:json_end])
                else:
                    raise ValueError("No se encontró formato JSON en la respuesta")
                
                logger.info(f"Clasificación generada para la actuación: {clasificacion_json.get('nivel_urgencia', 'No clasificada')}")
                return clasificacion_json
            
            except json.JSONDecodeError:
                logger.error("Error al decodificar la respuesta JSON")
                return {
                    "nivel_urgencia": "Normal",
                    "tipo_actuacion": "No clasificada",
                    "requiere_accion": False,
                    "justificacion": "No se pudo determinar automáticamente."
                }
        
        except Exception as e:
            logger.error(f"Error al clasificar actuación: {str(e)}")
            return {
                "nivel_urgencia": "Normal",
                "tipo_actuacion": "No clasificada",
                "requiere_accion": False,
                "justificacion": "No se pudo determinar automáticamente."
            }
    
    def _generar_resumen_simulado(self, detalle_proceso: Dict, actuaciones: List[Dict]) -> str:
        """Genera un resumen simulado para desarrollo sin API key."""
        radicado = detalle_proceso.get('llaveProceso', 'No especificado')
        despacho = detalle_proceso.get('despacho', 'No especificado')
        demandantes = ", ".join(detalle_proceso.get("demandantes", ["No especificado"]))
        demandados = ", ".join(detalle_proceso.get("demandados", ["No especificado"]))
        
        return f"""
        El proceso judicial con radicado {radicado} se encuentra actualmente en curso en el despacho {despacho}. Este proceso involucra a {demandantes} como parte demandante y a {demandados} como parte demandada.

        Según las actuaciones recientes, el proceso ha tenido avances significativos en los últimos meses. Se han registrado notificaciones importantes y se han cumplido los términos procesales establecidos. Las actuaciones más recientes sugieren que el proceso está siguiendo su curso normal dentro de los tiempos esperados para este tipo de casos.

        Es importante prestar atención a las próximas fechas de audiencia y a los requerimientos pendientes, ya que podrían ser determinantes para el desarrollo del proceso. Se recomienda mantener un seguimiento constante de las actuaciones futuras para asegurar el cumplimiento de todos los términos legales y evitar contratiempos procesales.
        """.strip()
    
    def _clasificar_actuacion_simulada(self, actuacion: Dict) -> Dict:
        """Clasifica una actuación de forma simulada para desarrollo sin API key."""
        texto_actuacion = actuacion.get('actuacion', '').lower()
        
        # Clasificación basada en palabras clave simples
        if any(palabra in texto_actuacion for palabra in ['audiencia', 'citación', 'comparecencia']):
            return {
                "nivel_urgencia": "Urgente",
                "tipo_actuacion": "Audiencia",
                "requiere_accion": True,
                "justificacion": "Las audiencias requieren preparación y asistencia obligatoria."
            }
        elif any(palabra in texto_actuacion for palabra in ['requerimiento', 'solicitud', 'plazo']):
            return {
                "nivel_urgencia": "Alta",
                "tipo_actuacion": "Requerimiento",
                "requiere_accion": True,
                "justificacion": "Existe un plazo definido para responder al requerimiento."
            }
        elif any(palabra in texto_actuacion for palabra in ['notificación', 'aviso', 'comunicación']):
            return {
                "nivel_urgencia": "Normal",
                "tipo_actuacion": "Notificación",
                "requiere_accion": False,
                "justificacion": "Es una notificación informativa que no requiere acción inmediata."
            }
        else:
            return {
                "nivel_urgencia": "Baja",
                "tipo_actuacion": "Trámite",
                "requiere_accion": False,
                "justificacion": "Actuación de trámite regular sin plazos críticos asociados."
            }
