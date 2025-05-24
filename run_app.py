"""
Script para iniciar la aplicación en modo producción.
Este archivo configura y ejecuta la aplicación con Uvicorn en modo producción.
"""

import os
import sys
from pathlib import Path
import uvicorn
import logging

# Agregar el directorio raíz al path para importar los módulos de la aplicación
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# Importar configuración de despliegue
from app.config_deploy import HOST, PORT, WORKERS, LOG_LEVEL, RELOAD

# Configuración de logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(root_dir, "app.log"))
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal para iniciar la aplicación."""
    logger.info(f"Iniciando aplicación en {HOST}:{PORT} con {WORKERS} workers")
    
    # Iniciar la aplicación con Uvicorn
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        workers=WORKERS,
        reload=RELOAD,
        log_level=LOG_LEVEL
    )

if __name__ == "__main__":
    main()
