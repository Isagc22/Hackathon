"""
Configuración de variables de entorno para la aplicación.
Este archivo establece las variables de entorno necesarias para la API de OpenAI.
"""

import os

# Configurar la clave de API de OpenAI
# En un entorno de producción, esta clave debería estar en un archivo .env o en variables de entorno del sistema
os.environ["OPENAI_API_KEY"] = "sk-demo-key-for-development-purposes-only"

# Configurar el modelo a utilizar
os.environ["OPENAI_MODEL"] = "gpt-3.5-turbo"
