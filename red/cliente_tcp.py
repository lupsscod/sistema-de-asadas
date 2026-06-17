import socket
from typing import Optional, List

class ClienteTCP:
    """Abstracción para gestionar la interacción del socket por el lado del cliente."""
    
    def __init__(self, ip_servidor: str = "127.0.0.1", puerto: int = 5000):
        self.ip_servidor = ip_servidor
        self.puerto = puerto
        self.socket_cliente: Optional[socket.socket] = None

    def conectar(self) -> bool:
        """Establece el canal de comunicaciones TCP/IP."""
        try:
            self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_cliente.connect((self.ip_servidor, self.puerto))
            return True
        except Exception as error:
            print(f"[Error de Red] Imposible conectar al servidor: {error}")
            return False

    def enviar_peticion(self, mensaje_comando: str) -> str:
        """Envía una instrucción formateada y espera el retorno síncrono."""
        if not self.socket_cliente:
            return "ERROR|No hay conexión activa con el servidor central."
        try:
            self.socket_cliente.sendall(mensaje_comando.encode('utf-8'))
            respuesta = self.socket_cliente.recv(8192)
            return respuesta.decode('utf-8')
        except Exception as error:
            return f"ERROR|Pérdida de enlace durante la transmisión: {error}"

    def cerrar(self) -> None:
        """Termina de forma limpia la sesión de red."""
        if self.socket_cliente:
            self.socket_cliente.close()