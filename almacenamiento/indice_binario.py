import struct
import os
from typing import List, Tuple

RUTA_INDICE = "datos/asadas.idx"
# Formato index: I (id, 4B) + Q (offset, 8B) = 12 Bytes fijos por nodo indexado
FORMATO_INDICE = ">IQ" 
TAMANIO_NODO_IDX = 12

def guardar_indice_lineal(lista_indices: List[Tuple[int, int]]) -> None:
    """Guarda en un archivo indexado plano las relaciones de llaves y offsets."""
    os.makedirs("datos", exist_ok=True)
    with open(RUTA_INDICE, "wb") as archivo:
        for id_asada, offset in lista_indices:
            archivo.write(struct.pack(FORMATO_INDICE, id_asada, offset))

def cargar_indice_lineal() -> List[Tuple[int, int]]:
    """Carga las llaves mapeadas desde el archivo de índices."""
    if not os.path.exists(RUTA_INDICE):
        return []
    lista_indices = []
    with open(RUTA_INDICE, "rb") as archivo:
        while True:
            bloque = archivo.read(TAMANIO_NODO_IDX)
            if not bloque or len(bloque) < TAMANIO_NODO_IDX:
                break
            id_asada, offset = struct.unpack(FORMATO_INDICE, bloque)
            lista_indices.append((id_asada, offset))
    return lista_indices