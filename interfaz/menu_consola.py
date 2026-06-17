import sys
from red.cliente_tcp import ClienteTCP
from geo.visualizador_osm import generar_mapa_asada_html

def mostrar_encabezado() -> None:
    print("\n" + "="*50)
    print("      SISTEMA DISTRIBUIDO DE CONSULTA - ASADAS CR      ")
    print("="*50)

def ejecutar_menu_interactivo(ip_servidor: str) -> None:
    """Administra los flujos de pantallas del menú por consola."""
    cliente = ClienteTCP(ip_servidor, 5000)
    if not cliente.conectar():
        print("[Fallo] Terminando cliente por falta de conexión remota.")
        return

    while True:
        mostrar_encabezado()
        print("1. Buscar ASADA por ID (Árbol de Búsqueda ABB)")
        print("2. Consultar por División Política (Multi-lista Enlazada)")
        print("3. Salir de la aplicación")
        opcion = input("\nSeleccione una opción de consulta (1-3): ").strip()

        if opcion == "1":
            id_ingresado = input("Digite el id_Asada a consultar de la ARESEP: ").strip()
            if not id_ingresado.isdigit():
                print("[!] El ID debe ser un value entero numérico.")
                continue

            respuesta = cliente.enviar_peticion(f"BUSCAR_ID|{id_ingresado}")
            
            datos = respuesta.split("@@")
            
            if datos[0] == "OK":
                print("\n" + "-"*35 + " REGISTRO HALLADO " + "-"*35)
                print(f"ID ASADA:   {datos[1]}")
                print(f"OPERADOR:   {datos[2]}")
                print(f"UBICACIÓN:  {datos[3]} -> {datos[4]} -> {datos[5]} (Código DTA: {datos[9]})")
                print(f"CONTACTO:   {datos[6]}")
                print(f"CRTM05 (X,Y): ({datos[7]}, {datos[8]})")
                print("-" * 88)
                
                ver_mapa = input("¿Desea generar el mapa geográfico en OpenStreetMap? (s/n): ").strip().lower()
                if ver_mapa == 's':
                    generar_mapa_asada_html(datos[2], float(datos[7]), float(datos[8]), datos[5])
            else:
                mensaje_error = datos[1] if len(datos) > 1 else "Error desconocido"
                print(f"\n[Aviso Servidor]: {mensaje_error}")

        elif opcion == "2":
            res_p = cliente.enviar_peticion("GET_PROVINCIAS")
            if res_p.startswith("ERROR") or not res_p.split("|")[1]:
                print("[!] No se pudieron recuperar las provincias del servidor.")
                continue
            provincias = res_p.split("|")[1].split(";")
            
            print("\n--- SELECCIONE PROVINCIA ---")
            for indice, prov in enumerate(provincias, 1):
                print(f"{indice}. {prov}")
            
            try:
                sel_p = int(input("Opción: ")) - 1
                if sel_p < 0 or sel_p >= len(provincias): raise ValueError
                provincia_seleccionada = provincias[sel_p]

                res_c = cliente.enviar_peticion(f"GET_CANTONES|{provincia_seleccionada}")
                cantones = res_c.split("|")[1].split(";")
                print(f"\n--- CANTONES DE {provincia_seleccionada} ---")
                for indice, cant in enumerate(cantones, 1):
                    print(f"{indice}. {cant}")
                sel_c = int(input("Opción: ")) - 1
                if sel_c < 0 or sel_c >= len(cantones): raise ValueError
                canton_seleccionado = cantones[sel_c]

                res_d = cliente.enviar_peticion(f"GET_DISTRITOS|{provincia_seleccionada}|{canton_seleccionado}")
                distritos = res_d.split("|")[1].split(";")
                print(f"\n--- DISTRITOS DE {canton_seleccionado} ---")
                for indice, dist in enumerate(distritos, 1):
                    print(f"{indice}. {dist}")
                sel_d = int(input("Opción: ")) - 1
                if sel_d < 0 or sel_d >= len(distritos): raise ValueError
                distrito_seleccionado = distritos[sel_d]
            except (ValueError, IndexError):
                print("[!] Selección inválida. Regresando al menú principal.")
                continue

            res_a = cliente.enviar_peticion(f"GET_ASADAS|{provincia_seleccionada}|{canton_seleccionado}|{distrito_seleccionado}")
            asadas_cruda = res_a.split("|")[1]
            
            if not asadas_cruda:
                print(f"\nNo existen ASADAS registradas para el distrito: {distrito_seleccionado}")
                continue

            asadas = asadas_cruda.split(";")
            print(f"\n=== ASADAS ASOCIADAS A {distrito_seleccionado} ===")
            mapeo_menu = {}
            for indice, item in enumerate(asadas, 1):
                id_a, nombre_a = item.split(":")
                print(f"{indice}. [ID: {id_a}] {nombre_a}")
                mapeo_menu[indice] = id_a

            sel_asada = input("\nSeleccione un número para inspeccionar detalles o presione Intro para volver: ").strip()
            if sel_asada.isdigit() and int(sel_asada) in mapeo_menu:
                id_remoto = mapeo_menu[int(sel_asada)]
                res_final = cliente.enviar_peticion(f"BUSCAR_ID|{id_remoto}")
                
                datos = res_final.split("@@")
                if datos[0] == "OK":
                    print("\n" + "-"*35 + " REGISTRO " + "-"*35)
                    print(f"ASADA: {datos[2]}\nCONTACTO: {datos[6]}\nCOOR: X={datos[7]}, Y={datos[8]}")
                    print("-" * 80)
                    ver_mapa = input("¿Desea mapear su ubicación geográfica? (s/n): ").strip().lower()
                    if ver_mapa == 's':
                        generar_mapa_asada_html(datos[2], float(datos[7]), float(datos[8]), datos[5])
                else:
                    print("[!] No se pudieron recuperar los detalles de la ASADA seleccionada.")

        elif opcion == "3":
            print("\n[Desconexión] Cerrando sesión de consultas remota.")
            cliente.cerrar()
            break
        else:
            print("[!] Opción inválida en el menú principal.")