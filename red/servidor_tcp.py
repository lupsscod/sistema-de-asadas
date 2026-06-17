import socket
import threading
from typing import Optional
from nucleo.arbol_busqueda import ArbolBusqueda
from nucleo.lista_enlazada import ListaJerarquicaPolitica
from almacenamiento.indice_binario import cargar_indice_lineal
from almacenamiento.archivo_binario import leer_registro_directo
from almacenamiento.sincronizador import ejecutar_sincronizacion_completa

# Configuraciones de red del servidor central
DIRECCION_HOST = "0.0.0.0"
PUERTO_HOST = 5000

# Estructuras globales del servidor en memoria
arbol_indice = ArbolBusqueda()
lista_politica = ListaJerarquicaPolitica()

def levantar_estructuras_memoria() -> None:
    """
    Carga los índices binarios desde disco hacia el ABB y la Multi-lista.
    Aplica una estrategia de bisección para garantizar un árbol balanceado.
    """
    print("[Servidor] Estructurando índices en memoria RAM...")
    indices = cargar_indice_lineal()
    
    if not indices:
        print("[Servidor] No se encontraron índices binarios para cargar.")
        return

    # 1. Insertar en el ABB usando bisección para evitar la degeneración del árbol (árbol en línea recta)
    def insertar_balanceado(inicio: int, fin: int):
        if inicio > fin:
            return
        # Encontrar el elemento central de la partición actual
        medio = (inicio + fin) // 2
        id_asada, offset = indices[medio]
        
        # Insertar el nodo central en el ABB
        arbol_indice.insertar(id_asada, offset)
        
        # Procesar de forma recursiva las mitades izquierda y derecha (Divide y Vencerás)
        insertar_balanceado(inicio, medio - 1)
        insertar_balanceado(medio + 1, fin)

    # Arrancar la inserción balanceada en el ABB
    insertar_balanceado(0, len(indices) - 1)
    print("[Servidor] Árbol Binario de Búsqueda (ABB) cargado y balanceado con éxito.")

    # 2. Cargar de forma lineal la Multi-lista Jerárquica de división política
    for id_asada, offset in indices:
        asada_objeto = leer_registro_directo(offset)
        if asada_objeto:
            lista_politica.insertar_asada(
                asada_objeto.provincia, asada_objeto.canton, asada_objeto.distrito,
                asada_objeto.id_asada, asada_objeto.nombre, offset
            )
    print("[Servidor] Multi-lista jerárquica cargada con éxito.")

def gestionar_solicitud_cliente(conexion: socket.socket, direccion: tuple) -> None:
    """Maneja las peticiones de un cliente remoto de manera independiente (Hilo)."""
    print(f"[Conexión] Nuevo cliente conectado desde: {direccion}")
    try:
        while True:
            datos_recibidos = conexion.recv(4096)
            if not datos_recibidos:
                break
            
            peticion = datos_recibidos.decode('utf-8').strip()
            partes = peticion.split("|")
            comando = partes[0]

            if comando == "BUSCAR_ID":
                id_buscar = int(partes[1])
                offset = arbol_indice.buscar(id_buscar)
                if offset is not None:
                    asada = leer_registro_directo(offset)
                    if asada:
                        # Protocolo unificado con @@ para evitar colisiones
                        respuesta = f"OK@@{asada.id_asada}@@{asada.nombre}@@{asada.provincia}@@{asada.canton}@@{asada.distrito}@@{asada.contacto}@@{asada.coord_x}@@{asada.coord_y}@@{asada.codigo_dta}"
                    else:
                        respuesta = "ERROR@@Fallo al leer datos del binario."
                else:
                    respuesta = "ERROR@@ID de ASADA no localizado en el ABB."

            elif comando == "GET_PROVINCIAS":
                provincias = lista_politica.obtener_provincias()
                respuesta = f"OK|{';'.join(provincias)}"

            elif comando == "GET_CANTONES":
                prov_nom = partes[1]
                cantones = lista_politica.obtener_cantones(prov_nom)
                respuesta = f"OK|{';'.join(cantones)}"

            elif comando == "GET_DISTRITOS":
                prov_nom = partes[1]
                cant_nom = partes[2]
                distritos = lista_politica.obtener_distritos(prov_nom, cant_nom)
                respuesta = f"OK|{';'.join(distritos)}"

            elif comando == "GET_ASADAS":
                prov_nom = partes[1]
                cant_nom = partes[2]
                dist_nom = partes[3]
                asadas_res = lista_politica.obtener_asadas(prov_nom, cant_nom, dist_nom)
                serializado = [f"{i[0]}:{i[1]}" for i in asadas_res]
                respuesta = f"OK|{';'.join(serializado)}"
            else:
                respuesta = "ERROR|Comando del protocolo no soportado."

            conexion.sendall(respuesta.encode('utf-8'))
    except Exception as error:
        print(f"[Aviso] Interrupción en sesión de cliente {direccion}: {error}")
    finally:
        conexion.close()
        print(f"[Conexión] Cliente {direccion} desconectado.")

def arrancar_servidor() -> None:
    """Ejecuta el ciclo de sincronización e inicia la escucha distribuida de sockets."""
    print("--- INICIANDO SERVIDOR CENTRAL ASADAS ---")
    ejecutar_sincronizacion_completa()
    levantar_estructuras_memoria()

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((DIRECCION_HOST, PUERTO_HOST))
    servidor.listen(10)
    print(f"[Servidor Activo] Escuchando solicitudes en puerto {PUERTO_HOST}...")

    try:
        while True:
            canal_cliente, dir_cliente = servidor.accept()
            hilo_hijo = threading.Thread(
                target=gestionar_solicitud_cliente, 
                args=(canal_cliente, dir_cliente), 
                daemon=True
            )
            hilo_hijo.start()
    except KeyboardInterrupt:
        print("\n[Servidor] Apagando servicios centrales.")
    finally:
        servidor.close()