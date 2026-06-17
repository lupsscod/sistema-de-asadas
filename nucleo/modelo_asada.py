import struct

class Asada:
    """
    Representa una entidad ASADA con sus atributos normalizados.

    Soporta la serialización y deserialización a bloques de bytes fijos
    de 256 bytes para su correcto almacenamiento en archivos binarios.
    """
    FORMATO_BINARIO = ">I60s30s30s30s62sdd8s"
    TAMANIO_REGISTRO = 256

    def __init__(self, id_asada: int, nombre: str, provincia: str, canton: str, 
                 distrito: str, contacto: str, coord_x: float, coord_y: float, codigo_dta: str):
        """Inicializa una instancia de la clase Asada."""
        self.id_asada = id_asada
        self.nombre = nombre.strip()
        self.provincia = provincia.strip()
        self.canton = canton.strip()
        self.distrito = distrito.strip()
        self.contacto = contacto.strip()
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.codigo_dta = codigo_dta.strip()

    def serializar(self) -> bytes:
        """
        Convierte el objeto Asada en una cadena de bytes de tamaño fijo.

        Retorna:
        --------
        bytes
            Bloque de 256 bytes listo para ser escrito en disco.
        """
        datos_empaquetados = struct.pack(
            self.FORMATO_BINARIO,
            self.id_asada,
            self.nombre.encode('utf-8')[:60].ljust(60, b'\x00'),
            self.provincia.encode('utf-8')[:30].ljust(30, b'\x00'),
            self.canton.encode('utf-8')[:30].ljust(30, b'\x00'),
            self.distrito.encode('utf-8')[:30].ljust(30, b'\x00'),
            self.contacto.encode('utf-8')[:62].ljust(62, b'\x00'),
            self.coord_x,
            self.coord_y,
            self.codigo_dta.encode('utf-8')[:8].ljust(8, b'\x00')
        )
        return datos_empaquetados.ljust(self.TAMANIO_REGISTRO, b'\x00')

    @classmethod
    def deserializar(cls, bloque_bytes: bytes) -> 'Asada':
        """
        Reconstruye un objeto Asada a partir de un bloque de bytes de tamaño fijo.

        Parámetros:
        bloque_bytes : bytes
            Bloque de 256 bytes extraído del archivo binario.

        Retorna:
        Asada
            Instancia con los datos cargados.
        """
        tamanio_util = struct.calcsize(cls.FORMATO_BINARIO)
        datos = struct.unpack(cls.FORMATO_BINARIO, bloque_bytes[:tamanio_util])
        
        return cls(
            id_asada=datos[0],
            nombre=datos[1].decode('utf-8').strip('\x00'),
            provincia=datos[2].decode('utf-8').strip('\x00'),
            canton=datos[3].decode('utf-8').strip('\x00'),
            distrito=datos[4].decode('utf-8').strip('\x00'),
            contacto=datos[5].decode('utf-8').strip('\x00'),
            coord_x=datos[6],
            coord_y=datos[7],
            codigo_dta=datos[8].decode('utf-8').strip('\x00')
        )