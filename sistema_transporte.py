import math
import heapq

# =====================================================================
# PARTE 1: BASE DE CONOCIMIENTO (Cap. 2 - Lógica y Hechos)
# =====================================================================
# Coordenadas espaciales (X, Y en km) de cada estación
ESTACIONES = {
    "Portal Norte":     (10, 20),
    "Calle 100":        (10, 15),
    "Calle 72":         (10, 10),
    "Calle 26":         (10, 5),
    "Estacion Central": (10, 0),
    "Portal Sur":       (10, -10),
    "Suba":             (4, 18),
    "Polo":             (7, 12),
    "Universidad":      (5, 4),
    "Terminal":         (2, -2)
    # --- KRISTINA: Nuevas estaciones ---
}

# Conexiones: (Origen, Destino, Tiempo_minutos, Linea)
CONEXIONES = [
    # Línea A (Troncal Principal)
    ("Portal Norte", "Calle 100", 6, "Linea A"),
    ("Calle 100", "Calle 72", 5, "Linea A"),
    ("Calle 72", "Calle 26", 6, "Linea A"),
    ("Calle 26", "Estacion Central", 5, "Linea A"),
    ("Estacion Central", "Portal Sur", 12, "Linea A"),

    # Línea B (Línea Occidental)
    ("Suba", "Polo", 8, "Linea B"),
    ("Polo", "Calle 72", 4, "Linea B"),
    ("Calle 72", "Universidad", 7, "Linea B"),
    ("Universidad", "Terminal", 9, "Linea B"),

    # Línea C (Conexión Transversal)
    ("Portal Norte", "Suba", 7, "Linea C"),
    ("Universidad", "Calle 26", 5, "Linea C"),
    ("Terminal", "Portal Sur", 8, "Linea C"),
    # --- KRISTINA: Nuevas conexiones ---
]


# =====================================================================
# PARTE 2: SISTEMA BASADO EN REGLAS (Cap. 3 - Inferencia Lógica)
# =====================================================================
class MotorDeReglas:
    PENALIZACION_TRANSBORDO = 4  # Regla: +4 min si cambia de línea
    # --- MIGUEL: Reglas de Tarifa ---

    @staticmethod
    def obtener_conexiones_validas(actual, linea_actual, visitados):
        sucesores = []
        for orig, dest, tiempo, linea in CONEXIONES:
            # Regla 1: Adyacencia bidireccional
            vecino = dest if orig == actual else (orig if dest == actual else None)
            
            # Regla 2: Anti-ciclos (no repetir estaciones del camino)
            if vecino and vecino not in visitados:
                # Regla 3: Penalización si hay transbordo entre líneas
                transbordo = (linea_actual is not None and linea_actual != linea)
                costo_paso = tiempo + (MotorDeReglas.PENALIZACION_TRANSBORDO if transbordo else 0)
                
                sucesores.append((vecino, linea, costo_paso))
        return sucesores


# =====================================================================
# PARTE 3: BÚSQUEDA HEURÍSTICA A* (Cap. 9 - Optimización)
# =====================================================================
def heuristica(est_a, est_b):
    """Calcula distancia en línea recta (Euclidiana) como heurística h(n)"""
    x1, y1 = ESTACIONES[est_a]
    x2, y2 = ESTACIONES[est_b]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def buscar_mejor_ruta(inicio, destino):
    """Algoritmo A*: f(n) = g(n) + h(n)"""
    # Cola de prioridad: (f, g, estacion, linea_actual, camino)
    cola = [(heuristica(inicio, destino), 0, inicio, None, [(inicio, None, 0)])]
    mejor_g = {inicio: 0}

    while cola:
        f, g, actual, linea_actual, camino = heapq.heappop(cola)

        if actual == destino:
            return camino, g

        visitados = {est for est, _, _ in camino}
        for vecino, nueva_linea, costo in MotorDeReglas.obtener_conexiones_validas(actual, linea_actual, visitados):
            nuevo_g = g + costo
            if vecino not in mejor_g or nuevo_g < mejor_g[vecino]:
                mejor_g[vecino] = nuevo_g
                nuevo_f = nuevo_g + heuristica(vecino, destino)
                heapq.heappush(cola, (nuevo_f, nuevo_g, vecino, nueva_linea, camino + [(vecino, nueva_linea, costo)]))

    return None, "No se encontro ruta disponible."


# =====================================================================
# INTERFAZ INTERACTIVA
# =====================================================================
def imprimir_ruta(origen, destino):
    print("\n" + "="*50)
    print(f" RUTA OPTIMA: [{origen}] --> [{destino}]")
    print("="*50)
    camino, costo_total = buscar_mejor_ruta(origen, destino)

    if camino is None:
        print(f" [!] Error: {costo_total}")
        return

    print(f" Tiempo Total Estimado: {costo_total:.1f} minutos\n")
    # --- MIGUEL: Mostrar Tarifa ---
    print(" Itinerario paso a paso:")
    for i, (estacion, linea, costo) in enumerate(camino):
        if i == 0:
            print(f"  [1] Salir desde: {estacion}")
        else:
            print(f"  [{i+1}] Tomar {linea} hacia -> {estacion} (+{costo} min)")
    print("="*50 + "\n")


def menu_interactivo():
    estaciones = list(ESTACIONES.keys())
    while True:
        print("\n" + "="*45)
        print("  SISTEMA INTELIGENTE DE TRANSPORTE MASIVO")
        print("="*45)
        for idx, est in enumerate(estaciones, start=1):
            print(f"  [{idx}] {est}")
        print("  [0] Salir")
        print("="*45)

        try:
            opc_orig = int(input("\n Selecciona numero de SALIDA: "))
            if opc_orig == 0: break
            opc_dest = int(input(" Selecciona numero de LLEGADA: "))
            if opc_dest == 0: break

            if 1 <= opc_orig <= len(estaciones) and 1 <= opc_dest <= len(estaciones):
                imprimir_ruta(estaciones[opc_orig-1], estaciones[opc_dest-1])
            else:
                print(" [!] Opcion fuera de rango.")
        except (ValueError, EOFError):
            break


if __name__ == "__main__":
    menu_interactivo()
