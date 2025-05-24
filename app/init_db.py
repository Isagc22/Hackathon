"""
Script para inicializar la base de datos.
Este archivo crea las tablas en la base de datos y configura los datos iniciales.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar los módulos de la aplicación
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from app.models.database import crear_tablas

def main():
    """Función principal para inicializar la base de datos."""
    print("Inicializando la base de datos...")
    
    # Crear las tablas
    crear_tablas()
    
    print("Base de datos inicializada correctamente.")

if __name__ == "__main__":
    main()
