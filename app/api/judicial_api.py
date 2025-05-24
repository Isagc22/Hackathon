"""
Cliente para la API de la Rama Judicial de Colombia.
Este módulo proporciona funciones para consultar procesos judiciales
a través de los endpoints públicos de la Rama Judicial.
"""

import requests
from typing import Dict, List, Optional, Any
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JudicialAPIClient:
    """Cliente para interactuar con la API de la Rama Judicial de Colombia."""
    
    BASE_URL = "https://consultaprocesos.ramajudicial.gov.co:448/api/v2"
    
    def __init__(self):
        """Inicializa el cliente de la API."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Realiza una solicitud a la API de la Rama Judicial.
        
        Args:
            endpoint: Ruta del endpoint a consultar.
            params: Parámetros de la consulta.
            
        Returns:
            Respuesta de la API en formato JSON.
            
        Raises:
            Exception: Si ocurre un error en la solicitud.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Capturar el mensaje de error de la API si está disponible
            error_msg = str(e)
            try:
                error_json = e.response.json()
                if "Message" in error_json:
                    error_msg = f"{error_msg} - {error_json['Message']}"
            except:
                pass
            
            logger.error(f"Error al realizar la solicitud a {url}: {error_msg}")
            raise Exception(f"Error en la consulta a la API: {error_msg}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al realizar la solicitud a {url}: {str(e)}")
            raise Exception(f"Error en la consulta a la API: {str(e)}")
    
    def consultar_por_razon_social(self, nombre: str, tipo_persona: str = "jur", 
                                  solo_activos: bool = True, 
                                  codificacion_despacho: str = "", 
                                  pagina: int = 1) -> Dict:
        """
        Consulta procesos por nombre o razón social.
        
        Args:
            nombre: Nombre o razón social a consultar.
            tipo_persona: Tipo de persona (jur para jurídica, nat para natural).
            solo_activos: Si se deben mostrar solo procesos activos.
            codificacion_despacho: Código del despacho judicial (requerido para evitar error de demasiados registros).
            pagina: Número de página para resultados paginados.
            
        Returns:
            Resultados de la consulta.
            
        Raises:
            Exception: Si la consulta es demasiado general o hay otros errores.
        """
        endpoint = "Procesos/Consulta/NombreRazonSocial"
        params = {
            "nombre": nombre,
            "tipoPersona": tipo_persona,
            "SoloActivos": solo_activos,
            "codificacionDespacho": codificacion_despacho,
            "pagina": pagina
        }
        
        logger.info(f"Consultando procesos para razón social: {nombre} (despacho: {codificacion_despacho or 'no especificado'})")
        try:
            return self._make_request(endpoint, params)
        except Exception as e:
            if "Hay más de mil registros con los criterios especificados" in str(e):
                logger.warning("La consulta devolvió demasiados resultados. Se requieren criterios más específicos.")
                raise Exception("La consulta es demasiado general. Por favor, especifique un código de despacho o un nombre más específico.")
            raise
    
    def consultar_por_radicado(self, numero: str, solo_activos: bool = False, pagina: int = 1) -> Dict:
        """
        Consulta un proceso por su número de radicado.
        
        Args:
            numero: Número de radicado del proceso.
            solo_activos: Si se deben mostrar solo procesos activos.
            pagina: Número de página para resultados paginados.
            
        Returns:
            Resultados de la consulta.
        """
        endpoint = "Procesos/Consulta/NumeroRadicacion"
        params = {
            "numero": numero,
            "SoloActivos": solo_activos,
            "pagina": pagina
        }
        
        logger.info(f"Consultando proceso con radicado: {numero}")
        return self._make_request(endpoint, params)
    
    def obtener_detalle_proceso(self, id_proceso: str) -> Dict:
        """
        Obtiene el detalle de un proceso específico.
        
        Args:
            id_proceso: Identificador único del proceso.
            
        Returns:
            Detalles del proceso.
        """
        endpoint = f"Proceso/Detalle/{id_proceso}"
        
        logger.info(f"Obteniendo detalles del proceso ID: {id_proceso}")
        return self._make_request(endpoint)
    
    def obtener_actuaciones_proceso(self, id_proceso: str) -> Dict:
        """
        Obtiene las actuaciones de un proceso específico.
        
        Args:
            id_proceso: Identificador único del proceso.
            
        Returns:
            Lista de actuaciones del proceso.
        """
        endpoint = f"Proceso/Actuaciones/{id_proceso}"
        
        logger.info(f"Obteniendo actuaciones del proceso ID: {id_proceso}")
        return self._make_request(endpoint)
    
    def obtener_documentos_actuacion(self, id_reg_actuacion: str) -> Dict:
        """
        Obtiene los documentos asociados a una actuación específica.
        
        Args:
            id_reg_actuacion: Identificador único de la actuación.
            
        Returns:
            Lista de documentos de la actuación.
        """
        endpoint = f"Proceso/DocumentosActuacion/{id_reg_actuacion}"
        
        logger.info(f"Obteniendo documentos de la actuación ID: {id_reg_actuacion}")
        return self._make_request(endpoint)
    
    def obtener_documento(self, id_reg_documento: str) -> bytes:
        """
        Descarga un documento específico.
        
        Args:
            id_reg_documento: Identificador único del documento.
            
        Returns:
            Contenido binario del documento.
            
        Raises:
            Exception: Si ocurre un error en la descarga.
        """
        endpoint = f"Descarga/Documento/{id_reg_documento}"
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            logger.info(f"Descargando documento ID: {id_reg_documento}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al descargar el documento {id_reg_documento}: {str(e)}")
            raise Exception(f"Error en la descarga del documento: {str(e)}")
