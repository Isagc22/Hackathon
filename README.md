# Monitor Judicial - Sistema de Monitoreo y Clasificación Automatizada de Procesos Judiciales

## Descripción

Monitor Judicial es una aplicación web que permite monitorear y clasificar automáticamente procesos judiciales utilizando inteligencia artificial generativa. La aplicación consulta la API de la Rama Judicial de Colombia para obtener información sobre procesos judiciales, genera resúmenes automáticos y clasifica las actuaciones según su urgencia.

## Características

- Consulta de procesos judiciales por razón social o número de radicado
- Visualización detallada de procesos y actuaciones judiciales
- Generación automática de resúmenes utilizando IA generativa
- Clasificación automática de actuaciones por nivel de urgencia
- Almacenamiento en base de datos para trazabilidad de la información

## Requisitos

- Python 3.11 o superior
- Dependencias listadas en requirements.txt

## Instalación

1. Clonar el repositorio o descomprimir el archivo zip
2. Crear un entorno virtual:
   
   python -m venv venv
   
3. Activar el entorno virtual:
   - En Windows: venv\Scripts\activate
   - En Linux/Mac: source venv/bin/activate
4. Instalar dependencias:
   
   pip install -r requirements.txt
   pip install python-multipart
   
5. Inicializar la base de datos:
   
   python app/init_db.py
   

## Ejecución

Para ejecutar la aplicación en modo desarrollo:


python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
xdg-open http://localhost:8000


Para ejecutar la aplicación en modo producción:


python run_app.py o xdg-open http://localhost:8000


## Estructura del Proyecto

- app/: Directorio principal de la aplicación
  - api/: Módulos para interacción con APIs externas
  - models/: Modelos de datos y configuración de base de datos
  - services/: Servicios de la aplicación (IA, base de datos)
  - templates/: Plantillas HTML para la interfaz web
  - static/: Archivos estáticos (CSS, JavaScript)
  - utils/: Utilidades y funciones auxiliares
  - main.py: Punto de entrada principal de la aplicación
  - config.py: Configuración de la aplicación
  - init_db.py: Script para inicializar la base de datos
- tests/: Pruebas automatizadas
- run_app.py: Script para ejecutar la aplicación en producción

## Uso

1. Acceder a la aplicación web a través de http://localhost:8000
2. Utilizar el formulario de búsqueda para consultar procesos por razón social o número de radicado
3. Explorar los detalles de los procesos y sus actuaciones
4. Revisar los resúmenes generados automáticamente y la clasificación de actuaciones

## Notas Importantes

- La aplicación utiliza un modo de simulación para la generación de resúmenes y clasificación con IA. Para utilizar OpenAI en producción, es necesario configurar una API key válida en app/config.py.
- La API de la Rama Judicial tiene limitaciones en cuanto al número de resultados que puede devolver. Para consultas muy generales, es recomendable especificar un código de despacho.

## Contacto

Para más información o soporte, contactar a:
- Email: proyecto@judicial-monitor.com 