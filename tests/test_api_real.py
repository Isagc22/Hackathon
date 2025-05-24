"""
Script para probar la integración con la API de la Rama Judicial.
Este módulo permite validar el funcionamiento del cliente de la API
con datos reales proporcionados por el usuario.
"""

import sys
import os
import json
from pathlib import Path

# Agregar el directorio raíz al path para importar los módulos de la aplicación
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from app.api.judicial_api import JudicialAPIClient

def guardar_resultado(data, nombre_archivo):
    """Guarda los resultados de la consulta en un archivo JSON."""
    ruta_archivo = os.path.join(root_dir, "tests", "resultados", f"{nombre_archivo}.json")
    os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
    
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Resultados guardados en: {ruta_archivo}")

def probar_consulta_persona():
    """Prueba la consulta por nombre de persona."""
    cliente = JudicialAPIClient()
    
    try:
        # Consultar procesos para la persona proporcionada por el usuario
        nombre = "Merly Seleni Consuegra Zambrano"
        print(f"Probando consulta para persona: {nombre}")
        
        # Probar con diferentes códigos de despacho
        despachos = ["", "11001", "05001", "76001"]
        
        for despacho in despachos:
            try:
                resultado = cliente.consultar_por_razon_social(
                    nombre=nombre, 
                    tipo_persona="nat",  # Persona natural
                    solo_activos=True,
                    codificacion_despacho=despacho
                )
                
                print(f"Consulta exitosa con despacho {despacho or 'vacío'}. Procesos encontrados: {resultado.get('cantidadRegistros', 0)}")
                guardar_resultado(resultado, f"consulta_persona_{despacho or 'sin_despacho'}")
                
                # Si hay resultados, obtener el detalle del primer proceso
                if resultado.get('procesos') and len(resultado['procesos']) > 0:
                    primer_proceso = resultado['procesos'][0]
                    id_proceso = primer_proceso.get('idProceso')
                    
                    if id_proceso:
                        print(f"Obteniendo detalle del proceso ID: {id_proceso}")
                        detalle = cliente.obtener_detalle_proceso(id_proceso)
                        guardar_resultado(detalle, "detalle_proceso_persona")
                        
                        print("Obteniendo actuaciones del proceso")
                        actuaciones = cliente.obtener_actuaciones_proceso(id_proceso)
                        guardar_resultado(actuaciones, "actuaciones_proceso_persona")
                        
                        return True
            except Exception as e:
                print(f"Error con despacho {despacho}: {str(e)}")
                continue
        
        print("No se encontraron resultados para la persona con ninguno de los despachos probados")
        return False
    except Exception as e:
        print(f"Error en la prueba de consulta por persona: {str(e)}")
        return False

def probar_consulta_radicado_real():
    """Prueba la consulta por número de radicado real."""
    cliente = JudicialAPIClient()
    
    try:
        # Consultar el radicado proporcionado por el usuario
        radicado = "05001400302320240139200"
        print(f"Probando radicado real: {radicado}")
        
        resultado = cliente.consultar_por_radicado(numero=radicado)
        
        print(f"Consulta exitosa. Procesos encontrados: {resultado.get('cantidadRegistros', 0)}")
        guardar_resultado(resultado, f"consulta_radicado_real")
        
        if resultado.get('cantidadRegistros', 0) > 0 and resultado.get('procesos'):
            primer_proceso = resultado['procesos'][0]
            id_proceso = primer_proceso.get('idProceso')
            
            if id_proceso:
                print(f"Obteniendo detalle del proceso ID: {id_proceso}")
                detalle = cliente.obtener_detalle_proceso(id_proceso)
                guardar_resultado(detalle, "detalle_proceso_radicado")
                
                print("Obteniendo actuaciones del proceso")
                actuaciones = cliente.obtener_actuaciones_proceso(id_proceso)
                guardar_resultado(actuaciones, "actuaciones_proceso_radicado")
                
                # Si hay actuaciones con documentos, obtener los documentos de la primera
                if actuaciones.get('actuaciones') and len(actuaciones['actuaciones']) > 0:
                    for actuacion in actuaciones['actuaciones']:
                        if actuacion.get('conDocumentos'):
                            id_actuacion = actuacion.get('idRegActuacion')
                            print(f"Obteniendo documentos de la actuación ID: {id_actuacion}")
                            documentos = cliente.obtener_documentos_actuacion(id_actuacion)
                            guardar_resultado(documentos, "documentos_actuacion_radicado")
                            break
            
            return True
        else:
            print("No se encontraron resultados para el radicado proporcionado")
            return False
    except Exception as e:
        print(f"Error en la prueba de radicado real: {str(e)}")
        return False

if __name__ == "__main__":
    # Crear directorio para tests si no existe
    os.makedirs(os.path.join(root_dir, "tests"), exist_ok=True)
    
    print("=== Iniciando pruebas de integración con datos reales ===")
    
    exito_persona = probar_consulta_persona()
    exito_radicado = probar_consulta_radicado_real()
    
    if exito_persona or exito_radicado:
        print("✅ Al menos una prueba completada exitosamente")
        if exito_persona:
            print("✓ La consulta por persona fue exitosa")
        else:
            print("⚠️ La consulta por persona falló")
        
        if exito_radicado:
            print("✓ La consulta por radicado fue exitosa")
        else:
            print("⚠️ La consulta por radicado falló")
    else:
        print("❌ Todas las pruebas fallaron")
