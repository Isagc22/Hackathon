"""
Módulo para la gestión de la base de datos.
Este archivo define los modelos y la configuración de la base de datos.
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from pathlib import Path

# Configuración de la base de datos
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'judicial_monitor.db')}"

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la base para los modelos
Base = declarative_base()

class Empresa(Base):
    """Modelo para almacenar información de empresas."""
    __tablename__ = "empresas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), index=True)
    tipo_persona = Column(String(10), default="jur")  # jur o nat
    nit = Column(String(20), unique=True, index=True, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Relaciones
    procesos = relationship("Proceso", back_populates="empresa")
    
    def __repr__(self):
        return f"<Empresa {self.nombre}>"

class Proceso(Base):
    """Modelo para almacenar información de procesos judiciales."""
    __tablename__ = "procesos"
    
    id = Column(Integer, primary_key=True, index=True)
    id_proceso_api = Column(String(50), unique=True, index=True)
    llave_proceso = Column(String(100), index=True)
    fecha_proceso = Column(DateTime, nullable=True)
    fecha_ultima_actuacion = Column(DateTime, nullable=True)
    despacho = Column(String(255), nullable=True)
    departamento = Column(String(100), nullable=True)
    sujetos_procesales = Column(Text, nullable=True)
    clase_proceso = Column(String(255), nullable=True)
    tipo_proceso = Column(String(255), nullable=True)
    subtipo_proceso = Column(String(255), nullable=True)
    ubicacion_expediente = Column(String(255), nullable=True)
    es_privado = Column(Boolean, default=False)
    demandantes = Column(JSON, nullable=True)
    demandados = Column(JSON, nullable=True)
    resumen_generado = Column(Text, nullable=True)
    fecha_consulta = Column(DateTime, default=datetime.now)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    
    # Relaciones
    empresa = relationship("Empresa", back_populates="procesos")
    actuaciones = relationship("Actuacion", back_populates="proceso")
    
    def __repr__(self):
        return f"<Proceso {self.llave_proceso}>"

class Actuacion(Base):
    """Modelo para almacenar información de actuaciones judiciales."""
    __tablename__ = "actuaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    id_reg_actuacion = Column(String(50), unique=True, index=True)
    cons_actuacion = Column(Integer, nullable=True)
    fecha_actuacion = Column(DateTime, nullable=True)
    actuacion = Column(String(255), nullable=True)
    anotacion = Column(Text, nullable=True)
    fecha_inicial = Column(DateTime, nullable=True)
    fecha_final = Column(DateTime, nullable=True)
    fecha_registro = Column(DateTime, nullable=True)
    con_documentos = Column(Boolean, default=False)
    proceso_id = Column(Integer, ForeignKey("procesos.id"))
    
    # Campos para la clasificación
    nivel_urgencia = Column(String(20), nullable=True)  # Urgente, Alta, Normal, Baja
    tipo_actuacion = Column(String(50), nullable=True)
    requiere_accion = Column(Boolean, default=False)
    justificacion = Column(Text, nullable=True)
    
    # Relaciones
    proceso = relationship("Proceso", back_populates="actuaciones")
    documentos = relationship("Documento", back_populates="actuacion")
    
    def __repr__(self):
        return f"<Actuacion {self.id_reg_actuacion}>"

class Documento(Base):
    """Modelo para almacenar información de documentos judiciales."""
    __tablename__ = "documentos"
    
    id = Column(Integer, primary_key=True, index=True)
    id_reg_documento = Column(String(50), unique=True, index=True)
    nombre_documento = Column(String(255), nullable=True)
    fecha_documento = Column(DateTime, nullable=True)
    fecha_publicacion = Column(DateTime, nullable=True)
    url_documento = Column(String(255), nullable=True)
    ruta_local = Column(String(255), nullable=True)
    actuacion_id = Column(Integer, ForeignKey("actuaciones.id"))
    
    # Relaciones
    actuacion = relationship("Actuacion", back_populates="documentos")
    
    def __repr__(self):
        return f"<Documento {self.nombre_documento}>"

# Función para obtener una sesión de la base de datos
def get_db():
    """Proporciona una sesión de la base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para crear todas las tablas
def crear_tablas():
    """Crea todas las tablas en la base de datos."""
    Base.metadata.create_all(bind=engine)
