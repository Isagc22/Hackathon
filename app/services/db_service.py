"""
Servicios para la gestión de datos en la base de datos.
Este módulo proporciona funciones para almacenar y recuperar información de procesos judiciales.
"""

import logging
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from app.models.database import Empresa, Proceso, Actuacion, Documento

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseService:
    """Servicio para la gestión de datos en la base de datos."""
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """
        Convierte una cadena de fecha en un objeto datetime.
        Maneja varios formatos de fecha, incluido el formato ISO con 'T00:00:00'.
        
        Args:
            date_str: Cadena de fecha a convertir.
            
        Returns:
            Objeto datetime o None si la conversión falla.
        """
        if not date_str:
            return None
            
        try:
            # Intentar primero con formato simple YYYY-MM-DD
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            try:
                # Intentar con formato ISO YYYY-MM-DDT00:00:00
                return datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
            except (ValueError, IndexError):
                try:
                    # Intentar con formato ISO completo
                    return datetime.fromisoformat(date_str)
                except ValueError:
                    logger.warning(f"No se pudo convertir la fecha: {date_str}")
                    return None
    
    @staticmethod
    def guardar_proceso(db: Session, datos_proceso: Dict, datos_empresa: Optional[Dict] = None) -> Proceso:
        """
        Guarda o actualiza un proceso judicial en la base de datos.
        
        Args:
            db: Sesión de la base de datos.
            datos_proceso: Datos del proceso judicial.
            datos_empresa: Datos de la empresa relacionada (opcional).
            
        Returns:
            Instancia del proceso guardado.
        """
        # Verificar si el proceso ya existe
        id_proceso_api = datos_proceso.get('idProceso')
        proceso_existente = db.query(Proceso).filter(Proceso.id_proceso_api == id_proceso_api).first()
        
        # Si existe, actualizar datos
        if proceso_existente:
            logger.info(f"Actualizando proceso existente: {id_proceso_api}")
            
            # Actualizar campos del proceso
            fecha_ultima_actuacion = DatabaseService.parse_date(datos_proceso.get('fechaUltimaActuacion'))
            if fecha_ultima_actuacion:
                proceso_existente.fecha_ultima_actuacion = fecha_ultima_actuacion
                
            proceso_existente.fecha_consulta = datetime.now()
            
            db.commit()
            db.refresh(proceso_existente)
            return proceso_existente
        
        # Si no existe, crear nuevo proceso
        logger.info(f"Creando nuevo proceso: {id_proceso_api}")
        
        # Procesar empresa si se proporciona
        empresa_id = None
        if datos_empresa:
            empresa = DatabaseService.guardar_empresa(db, datos_empresa)
            empresa_id = empresa.id
        
        # Crear nuevo proceso
        nuevo_proceso = Proceso(
            id_proceso_api=id_proceso_api,
            llave_proceso=datos_proceso.get('llaveProceso'),
            fecha_proceso=DatabaseService.parse_date(datos_proceso.get('fechaProceso')),
            fecha_ultima_actuacion=DatabaseService.parse_date(datos_proceso.get('fechaUltimaActuacion')),
            despacho=datos_proceso.get('despacho'),
            departamento=datos_proceso.get('departamento'),
            sujetos_procesales=datos_proceso.get('sujetosProcesales'),
            empresa_id=empresa_id,
            fecha_consulta=datetime.now()
        )
        
        db.add(nuevo_proceso)
        db.commit()
        db.refresh(nuevo_proceso)
        return nuevo_proceso
    
    @staticmethod
    def guardar_detalle_proceso(db: Session, id_proceso_api: str, detalle: Dict) -> Proceso:
        """
        Guarda o actualiza los detalles de un proceso judicial.
        
        Args:
            db: Sesión de la base de datos.
            id_proceso_api: ID del proceso en la API.
            detalle: Detalles del proceso.
            
        Returns:
            Instancia del proceso actualizado.
        """
        # Buscar el proceso
        proceso = db.query(Proceso).filter(Proceso.id_proceso_api == id_proceso_api).first()
        
        if not proceso:
            logger.warning(f"No se encontró el proceso {id_proceso_api} para actualizar detalles")
            return None
        
        # Actualizar campos de detalle
        proceso.clase_proceso = detalle.get('claseProceso')
        proceso.tipo_proceso = detalle.get('tipoProceso')
        proceso.subtipo_proceso = detalle.get('subTipoProceso')
        proceso.ubicacion_expediente = detalle.get('ubicacionExpediente')
        proceso.es_privado = detalle.get('esPrivado', False)
        
        # Guardar demandantes y demandados como JSON
        if 'demandantes' in detalle:
            proceso.demandantes = json.dumps(detalle['demandantes'])
        
        if 'demandados' in detalle:
            proceso.demandados = json.dumps(detalle['demandados'])
        
        db.commit()
        db.refresh(proceso)
        return proceso
    
    @staticmethod
    def guardar_resumen_proceso(db: Session, id_proceso_api: str, resumen: str) -> Proceso:
        """
        Guarda el resumen generado para un proceso.
        
        Args:
            db: Sesión de la base de datos.
            id_proceso_api: ID del proceso en la API.
            resumen: Resumen generado.
            
        Returns:
            Instancia del proceso actualizado.
        """
        # Buscar el proceso
        proceso = db.query(Proceso).filter(Proceso.id_proceso_api == id_proceso_api).first()
        
        if not proceso:
            logger.warning(f"No se encontró el proceso {id_proceso_api} para guardar resumen")
            return None
        
        # Actualizar resumen
        proceso.resumen_generado = resumen
        
        db.commit()
        db.refresh(proceso)
        return proceso
    
    @staticmethod
    def guardar_actuaciones(db: Session, id_proceso_api: str, actuaciones: List[Dict]) -> List[Actuacion]:
        """
        Guarda las actuaciones de un proceso judicial.
        
        Args:
            db: Sesión de la base de datos.
            id_proceso_api: ID del proceso en la API.
            actuaciones: Lista de actuaciones.
            
        Returns:
            Lista de actuaciones guardadas.
        """
        # Buscar el proceso
        proceso = db.query(Proceso).filter(Proceso.id_proceso_api == id_proceso_api).first()
        
        if not proceso:
            logger.warning(f"No se encontró el proceso {id_proceso_api} para guardar actuaciones")
            return []
        
        actuaciones_guardadas = []
        
        for act_data in actuaciones:
            # Verificar si la actuación ya existe
            id_reg_actuacion = act_data.get('idRegActuacion')
            actuacion_existente = db.query(Actuacion).filter(Actuacion.id_reg_actuacion == id_reg_actuacion).first()
            
            if actuacion_existente:
                # Actualizar actuación existente
                actuaciones_guardadas.append(actuacion_existente)
                continue
            
            # Crear nueva actuación
            nueva_actuacion = Actuacion(
                id_reg_actuacion=id_reg_actuacion,
                cons_actuacion=act_data.get('consActuacion'),
                fecha_actuacion=DatabaseService.parse_date(act_data.get('fechaActuacion')),
                actuacion=act_data.get('actuacion'),
                anotacion=act_data.get('anotacion'),
                fecha_inicial=DatabaseService.parse_date(act_data.get('fechaInicial')),
                fecha_final=DatabaseService.parse_date(act_data.get('fechaFinal')),
                fecha_registro=DatabaseService.parse_date(act_data.get('fechaRegistro')),
                con_documentos=act_data.get('conDocumentos', False),
                proceso_id=proceso.id
            )
            
            db.add(nueva_actuacion)
            actuaciones_guardadas.append(nueva_actuacion)
        
        db.commit()
        
        # Refrescar las actuaciones para obtener sus IDs
        for actuacion in actuaciones_guardadas:
            db.refresh(actuacion)
        
        return actuaciones_guardadas
    
    @staticmethod
    def guardar_clasificacion_actuacion(db: Session, id_reg_actuacion: str, clasificacion: Dict) -> Actuacion:
        """
        Guarda la clasificación de una actuación.
        
        Args:
            db: Sesión de la base de datos.
            id_reg_actuacion: ID de la actuación en la API.
            clasificacion: Datos de la clasificación.
            
        Returns:
            Instancia de la actuación actualizada.
        """
        # Buscar la actuación
        actuacion = db.query(Actuacion).filter(Actuacion.id_reg_actuacion == id_reg_actuacion).first()
        
        if not actuacion:
            logger.warning(f"No se encontró la actuación {id_reg_actuacion} para guardar clasificación")
            return None
        
        # Actualizar clasificación
        actuacion.nivel_urgencia = clasificacion.get('nivel_urgencia')
        actuacion.tipo_actuacion = clasificacion.get('tipo_actuacion')
        actuacion.requiere_accion = clasificacion.get('requiere_accion', False)
        actuacion.justificacion = clasificacion.get('justificacion')
        
        db.commit()
        db.refresh(actuacion)
        return actuacion
    
    @staticmethod
    def guardar_documentos(db: Session, id_reg_actuacion: str, documentos: List[Dict]) -> List[Documento]:
        """
        Guarda los documentos de una actuación.
        
        Args:
            db: Sesión de la base de datos.
            id_reg_actuacion: ID de la actuación en la API.
            documentos: Lista de documentos.
            
        Returns:
            Lista de documentos guardados.
        """
        # Buscar la actuación
        actuacion = db.query(Actuacion).filter(Actuacion.id_reg_actuacion == id_reg_actuacion).first()
        
        if not actuacion:
            logger.warning(f"No se encontró la actuación {id_reg_actuacion} para guardar documentos")
            return []
        
        documentos_guardados = []
        
        for doc_data in documentos:
            # Verificar si el documento ya existe
            id_reg_documento = doc_data.get('idRegDocumento')
            documento_existente = db.query(Documento).filter(Documento.id_reg_documento == id_reg_documento).first()
            
            if documento_existente:
                # Actualizar documento existente
                documentos_guardados.append(documento_existente)
                continue
            
            # Crear nuevo documento
            nuevo_documento = Documento(
                id_reg_documento=id_reg_documento,
                nombre_documento=doc_data.get('nombreDocumento'),
                fecha_documento=DatabaseService.parse_date(doc_data.get('fechaDocumento')),
                fecha_publicacion=DatabaseService.parse_date(doc_data.get('fechaPublicacion')),
                url_documento=f"https://consultaprocesos.ramajudicial.gov.co:448/api/v2/Descarga/Documento/{id_reg_documento}",
                actuacion_id=actuacion.id
            )
            
            db.add(nuevo_documento)
            documentos_guardados.append(nuevo_documento)
        
        db.commit()
        
        # Refrescar los documentos para obtener sus IDs
        for documento in documentos_guardados:
            db.refresh(documento)
        
        return documentos_guardados
    
    @staticmethod
    def guardar_empresa(db: Session, datos_empresa: Dict) -> Empresa:
        """
        Guarda o actualiza una empresa en la base de datos.
        
        Args:
            db: Sesión de la base de datos.
            datos_empresa: Datos de la empresa.
            
        Returns:
            Instancia de la empresa guardada.
        """
        nombre = datos_empresa.get('nombre')
        nit = datos_empresa.get('nit')
        
        # Buscar por NIT si está disponible
        if nit:
            empresa = db.query(Empresa).filter(Empresa.nit == nit).first()
            if empresa:
                return empresa
        
        # Buscar por nombre
        empresa = db.query(Empresa).filter(Empresa.nombre == nombre).first()
        
        if empresa:
            # Actualizar NIT si no lo tenía
            if nit and not empresa.nit:
                empresa.nit = nit
                db.commit()
                db.refresh(empresa)
            return empresa
        
        # Crear nueva empresa
        nueva_empresa = Empresa(
            nombre=nombre,
            tipo_persona=datos_empresa.get('tipo_persona', 'jur'),
            nit=nit
        )
        
        db.add(nueva_empresa)
        db.commit()
        db.refresh(nueva_empresa)
        return nueva_empresa
    
    @staticmethod
    def obtener_procesos_empresa(db: Session, empresa_id: int) -> List[Proceso]:
        """
        Obtiene todos los procesos de una empresa.
        
        Args:
            db: Sesión de la base de datos.
            empresa_id: ID de la empresa.
            
        Returns:
            Lista de procesos de la empresa.
        """
        return db.query(Proceso).filter(Proceso.empresa_id == empresa_id).all()
    
    @staticmethod
    def obtener_actuaciones_proceso(db: Session, proceso_id: int) -> List[Actuacion]:
        """
        Obtiene todas las actuaciones de un proceso.
        
        Args:
            db: Sesión de la base de datos.
            proceso_id: ID del proceso.
            
        Returns:
            Lista de actuaciones del proceso.
        """
        return db.query(Actuacion).filter(Actuacion.proceso_id == proceso_id).all()
    
    @staticmethod
    def obtener_documentos_actuacion(db: Session, actuacion_id: int) -> List[Documento]:
        """
        Obtiene todos los documentos de una actuación.
        
        Args:
            db: Sesión de la base de datos.
            actuacion_id: ID de la actuación.
            
        Returns:
            Lista de documentos de la actuación.
        """
        return db.query(Documento).filter(Documento.actuacion_id == actuacion_id).all()
