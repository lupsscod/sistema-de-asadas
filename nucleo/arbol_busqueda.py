from typing import Optional, Tuple

class NodoArbol:
    """Representa un nodo dentro del Árbol Binario de Búsqueda."""
    def __init__(self, id_asada: int, posicion_fisica: int):
        self.id_asada = id_asada
        self.posicion_fisica = posicion_fisica
        self.izquierdo: Optional[NodoArbol] = None
        self.derecho: Optional[NodoArbol] = None

class ArbolBusqueda:
    """Estructura de Árbol Binario de Búsqueda para indexación en memoria."""
    
    def __init__(self):
        """Inicializa un árbol de búsqueda vacío."""
        self.raiz: Optional[NodoArbol] = None

    def insertar(self, id_asada: int, posicion_fisica: int) -> None:
        """
        Inserta una nueva referencia de ASADA dentro del árbol.

        Parámetros:
        -----------
        id_asada : int
            Identificador único (llave primaria).
        posicion_fisica : int
            Offset de bytes dentro del archivo binario principal.
        """
        nuevo_nodo = NodoArbol(id_asada, posicion_fisica)
        if self.raiz is None:
            self.raiz = nuevo_nodo
        else:
            self._insertar_recursivo(self.raiz, nuevo_nodo)

    def _insertar_recursivo(self, nodo_actual: NodoArbol, nuevo_nodo: NodoArbol) -> None:
        if nuevo_nodo.id_asada < nodo_actual.id_asada:
            if nodo_actual.izquierdo is None:
                nodo_actual.izquierdo = nuevo_nodo
            else:
                self._insertar_recursivo(nodo_actual.izquierdo, nuevo_nodo)
        elif nuevo_nodo.id_asada > nodo_actual.id_asada:
            if nodo_actual.derecho is None:
                nodo_actual.derecho = nuevo_nodo
            else:
                self._insertar_recursivo(nodo_actual.derecho, nuevo_nodo)

    def buscar(self, id_asada: int) -> Optional[int]:
        """
        Busca un identificador en el árbol y retorna su offset físico en disco.

        Retorna:
        --------
        Optional[int]
            La posición en bytes si existe, de lo contrario None.
        """
        return self._buscar_recursivo(self.raiz, id_asada)

    def _buscar_recursivo(self, nodo_actual: Optional[NodoArbol], id_asada: int) -> Optional[int]:
        if nodo_actual is None:
            return None
        if id_asada == nodo_actual.id_asada:
            return nodo_actual.posicion_fisica
        elif id_asada < nodo_actual.id_asada:
            return self._buscar_recursivo(nodo_actual.izquierdo, id_asada)
        else:
            return self._buscar_recursivo(nodo_actual.derecho, id_asada)