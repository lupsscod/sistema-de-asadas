import os
from typing import Optional
from nucleo.modelo_asada import Asada

RUTA_BINARIO = "datos/asadas.bin"

def inicializar_entorno() -> None:
    """Asegura la existencia de la carpeta de almacenamiento local."""
    os.makedirs("datos", exist_ok=True)

def escribir_registro_secuencial(asada: Asada) -> int:
    """
    Guarda al final del archivo un registro de ASADA serializado.

    Retorna:
    --------
    int
        La posición de bytes (offset) donde inicia el nuevo registro.
    """
    inicializar_entorno()
    with open(RUTA_BINARIO, "ab") as archivo:
        posicion = archivo.tell()
        archivo.write(asada.serializar())
        return posicion

def leer_registro_directo(posicion_fisica: int) -> Optional[Asada]:
    """
    Recupera una ASADA en O(1) directo desde el archivo binario principal.

    Parámetros:
    -----------
    posicion_fisica : int
        El offset exacto de bytes del registro requerido.
    """
    if not os.path.exists(RUTA_BINARIO):
        return None
    with open(RUTA_BINARIO, "rb") as archivo:
        archivo.seek(posicion_fisica)
        bloque = archivo.read(Asada.TAMANIO_REGISTRO)
        if not bloque or len(bloque) < Asada.TAMANIO_REGISTRO:
            return None
        return Asada.deserializar(bloque)

def vaciar_archivo_principal() -> None:
    """Limpia o trunca por completo el repositorio físico binario."""
    inicializar_entorno()
    with open(RUTA_BINARIO, "wb") as archivo:
        archivo.truncate(0)