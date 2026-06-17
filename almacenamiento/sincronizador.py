import requests
import os
import json
from typing import Tuple, List
from nucleo.modelo_asada import Asada
from almacenamiento.archivo_binario import vaciar_archivo_principal, escribir_registro_secuencial
from almacenamiento.indice_binario import guardar_indice_lineal

URL_ENDPOINT = "https://datos.aresep.go.cr/ws.datosabiertos/Services/IA/Asadas.svc/ObtenerInformacionUbicacionAsadas"
RUTA_METADATOS = "datos/sincronizacion.json"

def requiere_actualizacion() -> Tuple[bool, List[dict]]:
    """
    Verifica mediante peticiones optimizadas si existen cambios remotos en ARESEP.
    """
    try:
        print("[Sincronizador] Conectando con el endpoint de la ARESEP...")
        respuesta = requests.get(URL_ENDPOINT, timeout=20)
        if respuesta.status_code != 200:
            print(f"[Sincronizador] Error de conexión HTTP: Código {respuesta.status_code}")
            return False, []
        
        datos_remotos = respuesta.json()
        
        if isinstance(datos_remotos, dict):
            if 'value' in datos_remotos:
                datos_remotos = datos_remotos['value']
            elif 'd' in datos_remotos:
                datos_remotos = datos_remotos['d']
            elif 'ObtenerInformacionUbicacionAsadasResult' in datos_remotos:
                datos_remotos = datos_remotos['ObtenerInformacionUbicacionAsadasResult']

        # Si viene serializado como un string de texto, lo forzamos a cargarse
        if isinstance(datos_remotos, str):
            datos_remotos = json.loads(datos_remotos)

        if not isinstance(datos_remotos, list):
            print("[Sincronizador] Error: El formato final decodificado no es una lista ejecutable.")
            return False, []

        longitud_actual = len(datos_remotos)
        print(f"[Sincronizador] Datos remotos detectados con éxito ({longitud_actual} registros).")
        
        if os.path.exists(RUTA_METADATOS):
            with open(RUTA_METADATOS, 'r') as archivo:
                metadatos_locales = json.load(archivo)
                if metadatos_locales.get("cantidad_registros") == longitud_actual:
                    return False, []
        
        return True, datos_remotos
    except Exception as error:
        print(f"[Error Sincronizador] Fallo crítico en comunicación: {error}")
        return False, []

def ejecutar_sincronizacion_completa() -> bool:
    """
    Descarga, normaliza y reconstruye rigurosamente los archivos físicos e índices.
    """
    necesita_cambio, datos = requiere_actualizacion()
    
    if not necesita_cambio and os.path.exists("datos/asadas.idx"):
        print("[Sincronizador] El almacenamiento local ya se encuentra al día con la ARESEP.")
        return False

    print("[Sincronizador] Iniciando procesamiento de limpieza y empaquetado binario...")
    vaciar_archivo_principal()
    mapeo_indices = []

    for elemento in datos:
        if not isinstance(elemento, dict):
            continue
            
        try:
            id_asada = elemento.get("id_Asada") or elemento.get("id_asada") or elemento.get("idAsada")
            if id_asada is None:
                continue

            nombre = elemento.get("operador") or elemento.get("Operador") or "ASADA SIN NOMBRE"
            provincia = elemento.get("provincia") or elemento.get("Provincia") or "DESCONOCIDA"
            canton = elemento.get("canton") or elemento.get("Canton") or "DESCONOCIDO"
            distrito = elemento.get("distrito") or elemento.get("Distrito") or "DESCONOCIDO"
            
            if not str(provincia).strip() or not str(canton).strip() or not str(distrito).strip():
                continue

            telefono = elemento.get("telefono") or elemento.get("Telefono") or "N/A"
            correo = elemento.get("correo") or elemento.get("Correo") or "N/A"
            contacto_formateado = f"Tel: {telefono} | Correo: {correo}"
            
            coord_x = elemento.get("coordenadaX") or elemento.get("coordenada_x") or 0.0
            coord_y = elemento.get("coordenadaY") or elemento.get("coordenada_y") or 0.0
            codigo_dta = elemento.get("codigoDTA") or elemento.get("codigo_dta") or "00000"

            objeto_asada = Asada(
                id_asada=int(id_asada),
                nombre=str(nombre).strip(),
                provincia=str(provincia).strip().upper(),
                canton=str(canton).strip().upper(),
                distrito=str(distrito).strip().upper(),
                contacto=str(contacto_formateado).strip(),
                coord_x=float(coord_x),
                coord_y=float(coord_y),
                codigo_dta=str(codigo_dta).strip()
            )

            offset_bytes = escribir_registro_secuencial(objeto_asada)
            mapeo_indices.append((objeto_asada.id_asada, offset_bytes))

        except Exception:
            continue

    if not mapeo_indices:
        print("[Sincronizador] ¡Alerta! Ningún registro superó los filtros de validación.")
        return False

    mapeo_indices.sort(key=lambda x: x[0])
    guardar_indice_lineal(mapeo_indices)

    with open(RUTA_METADATOS, 'w') as archivo:
        json.dump({"cantidad_registros": len(datos)}, archivo)

    print(f"[Sincronizador] Éxito absoluto. Se crearon todos los archivos binarios.")
    print(f"[Sincronizador] {len(mapeo_indices)} registros indexados correctamente en 'datos/asadas.idx'.")
    return True