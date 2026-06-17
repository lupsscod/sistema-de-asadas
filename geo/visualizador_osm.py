import os
import webbrowser
from pyproj import Transformer
import folium

def mapear_coordenadas_crtm05_a_wgs84(coor_x: float, coor_y: float) -> tuple:
    """
    Transforma coordenadas planas CRTM05 a coordenadas geográficas mundiales (WGS84).

    Retorna:
    --------
    tuple (latitud, longitud)
    """
    # EPSG:5367 corresponde al sistema cartográfico oficial de Costa Rica CRTM05
    # EPSG:4326 corresponde a WGS84 utilizado mundialmente por OpenStreetMap
    transformador = Transformer.from_crs("EPSG:5367", "EPSG:4326", always_xy=True)
    longitud, latitud = transformador.transform(coor_x, coor_y)
    return latitud, longitud

def generar_mapa_asada_html(nombre: str, x: float, y: float, distrito: str) -> None:
    """Crea un visor cartográfico OpenStreetMap para una única ASADA."""
    lat, lon = mapear_coordenadas_crtm05_a_wgs84(x, y)
    
    # Validar coordenadas por si vienen corruptas en el set original
    if lat == 0.0 or lon == 0.0 or abs(lat) > 90:
        print("[Geo Error] Coordenadas inválidas detectadas para mapeo.")
        return

    mapa_osm = folium.Map(location=[lat, lon], zoom_start=14, control_scale=True)
    folium.Marker(
        location=[lat, lon],
        popup=f"<b>ASADA:</b> {nombre}<br><b>Distrito:</b> {distrito}",
        tooltip=nombre,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(mapa_osm)

    os.makedirs("datos", exist_ok=True)
    ruta_archivo = os.path.abspath("datos/visor_asada.html")
    mapa_osm.save(ruta_archivo)
    
    print(f"[Geo] Renderizado exitoso. Abriendo visor geográfico...")
    webbrowser.open(f"file://{ruta_archivo}")