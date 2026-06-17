from typing import List, Optional, Tuple

class NodoAsadaLista:
    """Nodo final de la lista jerárquica que guarda datos de la ASADA."""
    def __init__(self, id_asada: int, nombre: str, posicion_fisica: int):
        self.id_asada = id_asada
        self.nombre = nombre
        self.posicion_fisica = posicion_fisica
        self.siguiente: Optional['NodoAsadaLista'] = None

class NodoDistrito:
    """Nodo intermedio que representa un Distrito."""
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.primer_nodo_asada: Optional[NodoAsadaLista] = None
        self.siguiente: Optional['NodoDistrito'] = None

class NodoCanton:
    """Nodo intermedio que representa un Cantón."""
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.primer_distrito: Optional[NodoDistrito] = None
        self.siguiente: Optional['NodoCanton'] = None

class NodoProvincia:
    """Nodo raíz de jerarquía que representa una Provincia."""
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.primer_canton: Optional[NodoCanton] = None
        self.siguiente: Optional['NodoProvincia'] = None

class ListaJerarquicaPolitica:
    """Maneja la multi-lista enlazada para estructurar la división política."""
    
    def __init__(self):
        self.primera_provincia: Optional[NodoProvincia] = None

    def insertar_asada(self, provincia_nom: str, canton_nom: str, distrito_nom: str, 
                       id_asada: int, nombre_asada: str, posicion_fisica: int) -> None:
        """Inserta ordenadamente una ASADA dentro de la estructura jerárquica."""
        prov = self._obtener_o_crear_provincia(provincia_nom)
        cant = self._obtener_o_crear_canton(prov, canton_nom)
        dist = self._obtener_o_crear_distrito(cant, distrito_nom)
        self._insertar_asada_en_distrito(dist, id_asada, nombre_asada, posicion_fisica)

    def _obtener_o_crear_provincia(self, nombre: str) -> NodoProvincia:
        actual = self.primera_provincia
        anterior = None
        while actual and actual.nombre != nombre:
            anterior = actual
            actual = actual.siguiente
        if actual:
            return actual
        nuevo = NodoProvincia(nombre)
        if anterior:
            anterior.siguiente = nuevo
        else:
            self.primera_provincia = nuevo
        return nuevo

    def _obtener_o_crear_canton(self, provincia: NodoProvincia, nombre: str) -> NodoCanton:
        actual = provincia.primer_canton
        anterior = None
        while actual and actual.nombre != nombre:
            anterior = actual
            actual = actual.siguiente
        if actual:
            return actual
        nuevo = NodoCanton(nombre)
        if anterior:
            anterior.siguiente = nuevo
        else:
            provincia.primer_canton = nuevo
        return nuevo

    def _obtener_o_crear_distrito(self, canton: NodoCanton, nombre: str) -> NodoDistrito:
        actual = canton.primer_distrito
        anterior = None
        while actual and actual.nombre != nombre:
            anterior = actual
            actual = actual.siguiente
        if actual:
            return actual
        nuevo = NodoDistrito(nombre)
        if anterior:
            anterior.siguiente = nuevo
        else:
            canton.primer_distrito = nuevo
        return nuevo

    def _insertar_asada_en_distrito(self, distrito: NodoDistrito, id_asada: int, 
                                    nombre: str, posicion_fisica: int) -> None:
        nuevo = NodoAsadaLista(id_asada, nombre, posicion_fisica)
        actual = distrito.primer_nodo_asada
        anterior = None
        # Mantener ordenado de manera ascendente por ID de ASADA
        while actual and actual.id_asada < id_asada:
            anterior = actual
            actual = actual.siguiente
        nuevo.siguiente = actual
        if anterior:
            anterior.siguiente = nuevo
        else:
            distrito.primer_nodo_asada = nuevo

    def obtener_provincias(self) -> List[str]:
        """Retorna los nombres de todas las provincias."""
        lista = []
        actual = self.primera_provincia
        while actual:
            lista.append(actual.nombre)
            actual = actual.siguiente
        return sorted(lista)

    def obtener_cantones(self, provincia_nom: str) -> List[str]:
        """Retorna los cantones de una provincia específica."""
        actual_p = self.primera_provincia
        while actual_p and actual_p.nombre != provincia_nom:
            actual_p = actual_p.siguiente
        if not actual_p:
            return []
        lista = []
        actual_c = actual_p.primer_canton
        while actual_c:
            lista.append(actual_c.nombre)
            actual_c = actual_c.siguiente
        return sorted(lista)

    def obtener_distritos(self, provincia_nom: str, canton_nom: str) -> List[str]:
        """Retorna los distritos de un cantón específico."""
        actual_p = self.primera_provincia
        while actual_p and actual_p.nombre != provincia_nom:
            actual_p = actual_p.siguiente
        if not actual_p:
            return []
        actual_c = actual_p.primer_canton
        while actual_c and actual_c.nombre != canton_nom:
            actual_c = actual_c.siguiente
        if not actual_c:
            return []
        lista = []
        actual_d = actual_c.primer_distrito
        while actual_d:
            lista.append(actual_d.nombre)
            actual_d = actual_d.siguiente
        return sorted(lista)

    def obtener_asadas(self, provincia_nom: str, canton_nom: str, distrito_nom: str) -> List[Tuple[int, str, int]]:
        """Retorna las parejas (id_asada, nombre, posicion_fisica) de un distrito."""
        actual_p = self.primera_provincia
        while actual_p and actual_p.nombre != provincia_nom:
            actual_p = actual_p.siguiente
        if not actual_p:
            return []
        actual_c = actual_p.primer_canton
        while actual_c and actual_c.nombre != canton_nom:
            actual_c = actual_c.siguiente
        if not actual_c:
            return []
        actual_d = actual_c.primer_distrito
        while actual_d and actual_d.nombre != distrito_nom:
            actual_d = actual_d.siguiente
        if not actual_d:
            return []
        lista = []
        actual_a = actual_d.primer_nodo_asada
        while actual_a:
            lista.append((actual_a.id_asada, actual_a.nombre, actual_a.posicion_fisica))
            actual_a = actual_a.siguiente
        return lista