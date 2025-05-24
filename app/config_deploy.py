"""
Archivo de configuración para el despliegue de la aplicación.
Este archivo contiene las configuraciones necesarias para el despliegue en producción.
"""

import os
from pathlib import Path

# Configuración de directorios
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "templates")

# Configuración de la aplicación
APP_NAME = "Monitor Judicial"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Sistema de monitoreo y clasificación automatizada de procesos judiciales con IA generativa"

# Configuración de la base de datos
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'judicial_monitor.db')}"

# Configuración del servidor
HOST = "0.0.0.0"
PORT = 8000
WORKERS = 4
RELOAD = False  # Desactivar en producción

# Configuración de logging
LOG_LEVEL = "info"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configuración de seguridad
ALLOWED_HOSTS = ["*"]  # Restringir en producción
