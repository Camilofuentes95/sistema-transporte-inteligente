"""
SISTEMA INTELIGENTE DE RUTAS DE TRANSPORTE MASIVO
Basado en:
- Cap. 2: Lógica y Representación del Conocimiento (Hechos y Relaciones)
- Cap. 3: Sistemas Basados en Reglas (Reglas Si-Entonces / Inferencia)
- Cap. 9: Búsquedas Heurísticas (Algoritmo A* / f(n) = g(n) + h(n))
"""

import math
import heapq

# =====================================================================
# 1. BASE DE CONOCIMIENTO (Capítulo 2: Lógica y Representación)
# =====================================================================
# Representamos el conocimiento mediante "Hechos" estructurados:
# a) Coordenadas espaciales de cada estación (X, Y en km para calcular la heurística).
ESTACIONES = {
    "Portal Norte": (10, 20),
    "Calle 100":    (10, 15),
    "Calle 72":     (10, 10),
    "Calle 26":     (10, 5),
    "Estacion Central": (10, 0),
    "Portal Sur":   (10, -10),
    "Suba":         (4, 18),
    "Polo":         (7, 12),
    "Universidad":  (5, 4),
    "Terminal":     (2, -2)
}

# b) Conexiones del sistema: (Origen, Destino, Tiempo_minutos, Linea)
# Equivalente lógico a: Conectado(A, B) ^ Costo(A, B, T) ^ Linea(A, B, L)
CONEXIONES = [
    # Línea A (Troncal Principal - Azul)
    ("Portal Norte", "Calle 100", 6, "Linea A"),
    ("Calle 100", "Calle 72", 5, "Linea A"),
    ("Calle 72", "Calle 26", 6, "Linea A"),
    ("Calle 26", "Estacion Central", 5, "Linea A"),
    ("Estacion Central", "Portal Sur", 12, "Linea A"),

    # Línea B (Línea Occidental - Verde)
    ("Suba", "Polo", 8, "Linea B"),
    ("Polo", "Calle 72", 4, "Linea B"),
    ("Calle 72", "Universidad", 7, "Linea B"),
    ("Universidad", "Terminal", 9, "Linea B"),

    # Línea C (Conexión Transversal - Naranja)
    ("Portal Norte", "Suba", 7, "Linea C"),
    ("Universidad", "Calle 26", 5, "Linea C"),
    ("Terminal", "Portal Sur", 8, "Linea C"),
]


# =====================================================================
# 2. SISTEMA BASADO EN REGLAS (Capítulo 3: Reglas de Inferencia)
# =====================================================================
class MotorDeReglas:
    """
    Aplica reglas lógicas de tipo SI <Condición> ENTONCES <Acción/Costo>
    para inferir los movimientos válidos y sus costos.
    """
    PENALIZACION_TRANSBORDO = 4  # 4 minutos por cambiar de línea

    @staticmethod
    def obtener_conexiones_validas(estacion_actual, linea_actual, visitados):
        """
        Regla 1 (Adyacencia Bidireccional):
        SI existe conexion(A, B) O conexion(B, A)
        Y B NO está en visitados (Regla Anti-Ciclos)
        ENTONCES B es un sucesor válido.
        """
        sucesores = []

        for origen, destino, tiempo, linea in CONEXIONES:
            siguiente = None
            if origen == estacion_actual:
                siguiente = destino
            elif destino == estacion_actual:
                siguiente = origen

            # Aplicar Regla Lógica: Solo avanzar si no es un ciclo
            if siguiente and siguiente not in visitados:
                # Regla 2 (Costo y Transbordos):
                # SI hay cambio de línea ENTONCES agregar penalización de tiempo
                costo_adicional = 0
                es_transbordo = False
                if linea_actual is not None and linea_actual != linea:
                    costo_adicional = MotorDeReglas.PENALIZACION_TRANSBORDO
                    es_transbordo = True

                costo_total_tramo = tiempo + costo_adicional
                sucesores.append({
                    "estacion": siguiente,
                    "costo": costo_total_tramo,
                    "linea": linea,
                    "transbordo": es_transbordo
                })

        return sucesores


# =====================================================================
# 3. BÚSQUEDA HEURÍSTICA A* (Capítulo 9: Algoritmos de Búsqueda)
# =====================================================================
def heuristica_distancia(estacion_a, estacion_b):
    """
    Función Heurística h(n):
    Estima el tiempo restante en línea recta (Distancia Euclidiana)
    Asumiendo una velocidad promedio de 1 km por minuto.
    Es admisible porque nunca sobreestima el costo real.
    """
    x1, y1 = ESTACIONES[estacion_a]
    x2, y2 = ESTACIONES[estacion_b]
    distancia_km = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    tiempo_estimado_minutos = distancia_km * 1.0  # h(n)
    return tiempo_estimado_minutos


def buscar_mejor_ruta(inicio, destino):
    """
    Algoritmo A* (A-Estrella):
    f(n) = g(n) + h(n)
    - g(n): Costo acumulado real desde el inicio hasta el nodo n.
    - h(n): Estimación heurística desde el nodo n hasta el destino.
    """
    if inicio not in ESTACIONES or destino not in ESTACIONES:
        return None, "Una o ambas estaciones no existen en la base de conocimiento."

    # Cola de prioridad: almacena tuplas (f_n, g_n, estacion_actual, linea_actual, camino)
    cola_prioridad = []
    
    # Estado inicial
    h_inicio = heuristica_distancia(inicio, destino)
    # (f(n), g(n), estacion, linea, camino_recorrido)
    heapq.heappush(cola_prioridad, (h_inicio, 0, inicio, None, [(inicio, None, 0)]))
    
    # Registro de mejores costos conocidos g(n) para cada estación
    mejor_costo_g = {inicio: 0}

    while cola_prioridad:
        f_actual, g_actual, actual, linea_actual, camino = heapq.heappop(cola_prioridad)

        # SI alcanzamos el destino -> Meta lograda (Camino Óptimo Encontrado)
        if actual == destino:
            return camino, g_actual

        # Extraer estaciones ya visitadas en este camino para no ciclar
        visitados_en_camino = {est for est, _, _ in camino}

        # Consultar al Motor de Reglas lógicas para obtener siguientes pasos
        sucesores = MotorDeReglas.obtener_conexiones_validas(actual, linea_actual, visitados_en_camino)

        for suc in sucesores:
            vecino = suc["estacion"]
            costo_paso = suc["costo"]
            nueva_linea = suc["linea"]

            nuevo_g = g_actual + costo_paso
            
            # Si encontramos un camino más corto hacia 'vecino'
            if vecino not in mejor_costo_g or nuevo_g < mejor_costo_g[vecino]:
                mejor_costo_g[vecino] = nuevo_g
                h_vecino = heuristica_distancia(vecino, destino)
                nuevo_f = nuevo_g + h_vecino
                
                nuevo_camino = camino + [(vecino, nueva_linea, costo_paso)]
                heapq.heappush(cola_prioridad, (nuevo_f, nuevo_g, vecino, nueva_linea, nuevo_camino))

    return None, "No se encontró ruta disponible entre los puntos seleccionados."


# =====================================================================
# 4. INTERFAZ INTERACTIVA Y VISUALIZACIÓN DE RESULTADOS
# =====================================================================
def imprimir_ruta(origen, destino):
    print("\n" + "="*55)
    print(f" BUSCANDO LA MEJOR RUTA: [{origen}] --> [{destino}]")
    print("="*55)
    
    camino, costo_total = buscar_mejor_ruta(origen, destino)

    if camino is None:
        print(f" [!] Error: {costo_total}")
        return

    print(f" Tiempo Total Estimado: {costo_total:.1f} minutos\n")
    print(" Itinerario paso a paso:")
    
    for i, (estacion, linea, costo) in enumerate(camino):
        if i == 0:
            print(f"  [Paso 1] Partir desde: {estacion}")
        else:
            print(f"  [Paso {i+1}] Tomar {linea} hacia -> {estacion} (+{costo} min)")
    print("="*55 + "\n")


def menu_interactivo():
    lista_estaciones = list(ESTACIONES.keys())
    
    while True:
        print("\n" + "="*50)
        print("   SISTEMA INTELIGENTE DE TRANSPORTE MASIVO")
        print("="*50)
        print("Estaciones disponibles:")
        for idx, est in enumerate(lista_estaciones, start=1):
            print(f"  [{idx}] {est}")
        print("  [0] Salir")
        print("="*50)

        # 1. Seleccionar salida
        try:
            opc_origen = int(input("\n Selecciona el numero de la estacion de SALIDA: "))
            if opc_origen == 0:
                print("Buen viaje!")
                break
            if not (1 <= opc_origen <= len(lista_estaciones)):
                print(" [!] Opcion invalida. Intenta nuevamente.")
                continue
            origen = lista_estaciones[opc_origen - 1]

            # 2. Seleccionar llegada
            opc_destino = int(input(" Selecciona el numero de la estacion de LLEGADA: "))
            if opc_destino == 0:
                print("Buen viaje!")
                break
            if not (1 <= opc_destino <= len(lista_estaciones)):
                print(" [!] Opcion invalida. Intenta nuevamente.")
                continue
            destino = lista_estaciones[opc_destino - 1]

            if origen == destino:
                print(" [!] La estacion de salida y llegada son la misma.")
                continue

            # Calcular y mostrar la ruta óptima
            imprimir_ruta(origen, destino)

        except (ValueError, EOFError):
            print(" [!] Entrada invalida.")
            break


if __name__ == "__main__":
    menu_interactivo()


