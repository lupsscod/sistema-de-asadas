import sys
from red.servidor_tcp import arrancar_servidor
from interfaz.menu_consola import ejecutar_menu_interactivo

if __name__ == "__main__":
    """
    Punto de entrada principal del sistema de ASADAS.
    Permite discriminar la ejecución mediante argumentos por consola.
    """
    if len(sys.argv) < 2:
        print("\nModo de uso incorrecto.")
        print("Para levantar el Servidor Central: python main.py servidor")
        print("Para levantar el Cliente de Consulta: python main.py cliente [IP_SERVIDOR]")
        sys.exit(1)

    rol = sys.argv[1].lower()

    if rol == "servidor":
        arrancar_servidor()
    elif rol == "cliente":
        ip = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
        ejecutar_menu_interactivo(ip)
    else:
        print(f"[!] Rol '{rol}' desconocido. Use 'servidor' o 'cliente'.")