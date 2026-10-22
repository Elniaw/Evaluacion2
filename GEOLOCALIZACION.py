import os
import requests
import urllib.parse

ROUTE_URL = "https://graphhopper.com/api/1/route?"
GEOCODE_URL = "https://graphhopper.com/api/1/geocode?"

def geocodificar(ubicacion, key):
    while ubicacion.strip() == "":
        ubicacion = input("Ingresa nuevamente la ubicación: ")
    url = GEOCODE_URL + urllib.parse.urlencode(
        {"q": ubicacion, "limit": "1", "locale": "es", "key": key}
    )
    resp = requests.get(url)
    datos = resp.json()
    if resp.status_code == 200 and len(datos["hits"]) != 0:
        h = datos["hits"][0]
        lat, lng = h["point"]["lat"], h["point"]["lng"]
        nombre = h["name"]
        partes = [h.get(c) for c in ("city", "state", "country") if h.get(c)]
        print(f"URL de geocodificación para {nombre}, {', '.join(partes)}")
        print(url)
        return resp.status_code, lat, lng, nombre
    print(f"Error de geocodificación (código {resp.status_code}). Mensaje: {datos.get('message', 'sin mensaje')}")
    return resp.status_code, "null", "null", ubicacion

def main():
    key = os.environ.get("GRAPHHOPPER_KEY") or input("Ingresa tu API key de GraphHopper: ").strip()
    vehiculos = {"auto": "car", "bicicleta": "bike", "a pie": "foot"}

    while True:
        print("\n+++++++++++++++++++++++++++++++++++++++++++++")
        print("Tipos de transporte disponibles: auto, bicicleta, a pie")
        print("+++++++++++++++++++++++++++++++++++++++++++++")
        elegido = input("Ingresa un tipo de transporte (s/salir para terminar): ").strip().lower()
        if elegido in ("s", "salir"):
            print("¡Hasta luego!")
            break
        vehiculo = vehiculos.get(elegido)
        if vehiculo is None:
            vehiculo = "car"
            print("No se ingresó un transporte válido. Se usará 'auto'.")

        origen = input("Ubicación de origen (s/salir para terminar): ").strip()
        if origen.lower() in ("s", "salir"):
            print("¡Hasta luego!")
            break
        o = geocodificar(origen, key)

        destino = input("Destino (s/salir para terminar): ").strip()
        if destino.lower() in ("s", "salir"):
            print("¡Hasta luego!")
            break
        d = geocodificar(destino, key)

        print("=================================================")
        if o[0] == 200 and d[0] == 200:
            params = [("point", f"{o[1]},{o[2]}"), ("point", f"{d[1]},{d[2]}")]
            url = ROUTE_URL + urllib.parse.urlencode(
                params + [("key", key), ("vehicle", vehiculo), ("locale", "es")]
            )
            resp = requests.get(url)
            datos = resp.json()
            print(f"Estado de la API de rutas: {resp.status_code}")
            print(f"URL de la API de rutas:\n{url}")
            print("=================================================")
            print(f"Indicaciones desde {o[3]} hasta {d[3]} en {elegido or 'auto'}")
            print("=================================================")
            if resp.status_code == 200:
                ruta = datos["paths"][0]
                km = ruta["distance"] / 1000
                millas = km / 1.61
                seg = int(ruta["time"] / 1000)
                print(f"Distancia recorrida: {millas:.2f} millas / {km:.2f} km")
                print(f"Duración del viaje: {seg // 3600:02d}:{(seg // 60) % 60:02d}:{seg % 60:02d}")
                print("=================================================")
                print("Narrativa del viaje:")
                for paso in ruta["instructions"]:
                    dist_km = paso["distance"] / 1000
                    print(f"- {paso['text']} ( {dist_km:.2f} km / {dist_km / 1.61:.2f} millas )")
                print("=============================================")
            else:
                print(f"Mensaje de error: {datos.get('message', 'sin mensaje')}")
                print("*************************************************")

if __name__ == "__main__":
    main()