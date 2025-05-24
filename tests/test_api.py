"""
Script para probar la integración con la API de la Rama Judicial.
Este módulo permite validar el funcionamiento del cliente de la API.
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

def probar_consulta_razon_social():
    """Prueba la consulta por razón social."""
    cliente = JudicialAPIClient()
    
    # Lista de empresas y códigos de despacho para probar
    empresas = [
        {"nombre": "Empresa Pequeña Ficticia SAS", "despacho": "11001"},  # Bogotá
        {"nombre": "Empresa Local Test", "despacho": "05001"},  # Medellín
        {"nombre": "Microempresa Prueba", "despacho": "76001"}   # Cali
    ]
    
    for empresa in empresas:
        try:
            print(f"Probando consulta para: {empresa['nombre']} en despacho: {empresa['despacho']}")
            resultado = cliente.consultar_por_razon_social(
                nombre=empresa['nombre'], 
                tipo_persona="jur", 
                solo_activos=True,
                codificacion_despacho=empresa['despacho']
            )
            
            print(f"Consulta exitosa. Procesos encontrados: {resultado.get('cantidadRegistros', 0)}")
            guardar_resultado(resultado, f"consulta_razon_social_{empresa['despacho']}")
            
            # Si hay resultados, obtener el detalle del primer proceso
            if resultado.get('procesos') and len(resultado['procesos']) > 0:
                primer_proceso = resultado['procesos'][0]
                id_proceso = primer_proceso.get('idProceso')
                
                if id_proceso:
                    print(f"Obteniendo detalle del proceso ID: {id_proceso}")
                    detalle = cliente.obtener_detalle_proceso(id_proceso)
                    guardar_resultado(detalle, "detalle_proceso")
                    
                    print("Obteniendo actuaciones del proceso")
                    actuaciones = cliente.obtener_actuaciones_proceso(id_proceso)
                    guardar_resultado(actuaciones, "actuaciones_proceso")
                    
                    return True
        except Exception as e:
            print(f"Error con empresa {empresa['nombre']}: {str(e)}")
            continue
    
    print("No se encontraron resultados para ninguna de las empresas probadas")
    return False

def probar_consulta_radicado():
    """Prueba la consulta por número de radicado."""
    cliente = JudicialAPIClient()
    
    # Lista de radicados para probar
    radicados = [
        "11001400300320230051800",
        "05001310301020220022900",
        "76001400300120210032300"
    ]
    
    for radicado in radicados:
        try:
            print(f"Probando radicado: {radicado}")
            resultado = cliente.consultar_por_radicado(numero=radicado)
            
            print(f"Consulta exitosa. Procesos encontrados: {resultado.get('cantidadRegistros', 0)}")
            guardar_resultado(resultado, f"consulta_radicado_{radicado}")
            
            if resultado.get('cantidadRegistros', 0) > 0:
                return True
        except Exception as e:
            print(f"Error con radicado {radicado}: {str(e)}")
            continue
    
    print("No se encontraron resultados para ninguno de los radicados probados")
    return False

if __name__ == "__main__":
    # Crear directorio para tests si no existe
    os.makedirs(os.path.join(root_dir, "tests"), exist_ok=True)
    
    print("=== Iniciando pruebas de integración con la API de la Rama Judicial ===")
    
    exito_razon_social = probar_consulta_razon_social()
    exito_radicado = probar_consulta_radicado()
    
    if exito_razon_social or exito_radicado:
        print("✅ Al menos una prueba completada exitosamente")
        if not exito_razon_social:
            print("⚠️ La consulta por razón social falló")
        if not exito_radicado:
            print("⚠️ La consulta por radicado falló")
    else:
        print("❌ Todas las pruebas fallaron")
