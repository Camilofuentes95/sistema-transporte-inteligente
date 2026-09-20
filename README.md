# Sistema Inteligente de Rutas de Transporte Masivo

Sistema inteligente desarrollado en **Python** para la determinación y optimización de rutas en redes de transporte masivo, fundamentado en representación del conocimiento, sistemas basados en reglas y búsqueda heurística informada ($A^*$).

---

## Marco Teórico y Referencias

El proyecto implementa los conceptos fundamentales descritos en la literatura académica:

> **Benítez, R. (2014).** *Inteligencia artificial avanzada*. Barcelona: Editorial UOC.
> * **Capítulo 2:** Lógica y representación del conocimiento (Hechos estructurados y relaciones espaciales).
> * **Capítulo 3:** Sistemas basados en reglas (Inferencia lógica SI-ENTONCES, transbordos y prevención de ciclos).
> * **Capítulo 9:** Técnicas basadas en búsquedas heurísticas (Algoritmo $A^*$ y heurística admisible).

---

## Arquitectura del Sistema

```
┌───────────────────────────────────────────────────────────┐
│               1. BASE DE CONOCIMIENTO                     │
│  - Estaciones: Coordenadas (X, Y) en km                   │
│  - Conexiones: Aristas del grafo con tiempos y líneas     │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│               2. MOTOR DE REGLAS (RBS)                    │
│  - Regla 1 (Adyacencia): Movilidad bidireccional          │
│  - Regla 2 (Anti-ciclos): Poda de estados repetidos       │
│  - Regla 3 (Transbordos): Penalización de tiempo (+4 min) │
│  - Regla 4 (Tarifas): Tarifa base + transbordo integrado  │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│              3. BÚSQUEDA HEURÍSTICA A*                    │
│  - Función de evaluación: f(n) = g(n) + h(n)              │
│  - g(n): Costo acumulado real (tiempo de viaje)           │
│  - h(n): Distancia euclidiana en línea recta al destino   │
│  - Exploración prioritaria con cola de prioridad (heapq)  │
└───────────────────────────────────────────────────────────┘
```

---

## ¿Cómo Funciona el Código? (Explicación Detallada)

El sistema opera a través de 3 componentes modulares que interactúan de forma secuencial:

### 1. Base de Conocimiento (Capítulo 2)
El conocimiento del mundo real se estructura en dos conjuntos de hechos:
* **`ESTACIONES`:** Un diccionario donde cada clave es el nombre de la estación y su valor es una tupla `(X, Y)` que representa su ubicación geográfica en kilómetros. Estas coordenadas son indispensables para que el algoritmo pueda calcular distancias geométricas reales hacia el destino.
* **`CONEXIONES`:** Una lista de tuplas con el formato `(Origen, Destino, Tiempo_minutos, Linea)`. Define las vías del sistema, el tiempo estándar de desplazamiento y la línea a la que pertenece cada tramo.

### 2. Motor de Reglas e Inferencia (Capítulo 3)
La clase `MotorDeReglas` aplica reglas lógicas de producción del tipo **SI `<condición>` ENTONCES `<acción/costo>`**:
* **Regla 1 (Adyacencia Bidireccional):** `SI` existe una conexión entre la estación $A$ y la estación $B$, `ENTONCES` el vehículo puede transitar en ambos sentidos ($A \rightarrow B$ o $B \rightarrow A$).
* **Regla 2 (Prevención de Ciclos):** `SI` una estación vecina ya forma parte del camino recorrido en la rama actual, `ENTONCES` se descarta para evitar bucles infinitos.
* **Regla 3 (Penalización por Transbordo):** `SI` la línea del tramo actual es diferente a la línea previa del pasajero, `ENTONCES` se suma un costo adicional de **+4 minutos** al tiempo del tramo (tiempo estimado de caminata y espera en el andén).
* **Regla 4 (Tarifa Económica):** `SI` el viaje es válido, `ENTONCES` se aplica una tarifa base ($2.950 COP) más un recargo fijo ($200 COP) por cada transbordo entre líneas diferentes.

### 3. Búsqueda Heurística A* (Capítulo 9)
Para encontrar la ruta más rápida sin explorar caminos innecesarios:
* **Función Heurística $h(n)$ (`heuristica`):** Calcula la distancia euclidiana en línea recta desde la estación actual $(X_1, Y_1)$ hasta la estación destino $(X_2, Y_2)$ usando el teorema de Pitágoras:
  $$h(n) = \sqrt{(X_1 - X_2)^2 + (Y_1 - Y_2)^2}$$
  Es una heurística **admisible** porque la distancia en línea recta nunca sobreestima el costo real.
* **Función de Evaluación $f(n) = g(n) + h(n)$:**
  * $g(n)$: Tiempo real acumulado desde el origen hasta el nodo $n$ (incluyendo penalizaciones por transbordo).
  * $h(n)$: Estimación heurística de tiempo restante hasta el destino.
* **Exploración con Cola de Prioridad (`heapq`):** En cada paso se extrae y expande el nodo con el menor valor de $f(n)$, garantizando encontrar la solución óptima en el menor número de pasos.

---

## Requisitos e Instalación

* **Python 3.8+** (No requiere dependencias externas; utiliza librerías estándar `math` y `heapq`).

### Clonar el Repositorio
```bash
git clone https://github.com/Camilofuentes95/sistema-transporte-inteligente.git
cd sistema-transporte-inteligente
```

---

## Uso y Ejecución

Ejecuta el script principal en la terminal:

```bash
python sistema_transporte.py
```

### Ejemplo de Salida Interactiva

```text
=============================================
  SISTEMA INTELIGENTE DE TRANSPORTE MASIVO
=============================================
  [1] Portal Norte
  [2] Calle 100
  [3] Calle 72
  [4] Calle 26
  [5] Estacion Central
  [6] Portal Sur
  [7] Suba
  [8] Polo
  [9] Universidad
  [10] Terminal
  [0] Salir
=============================================

 Selecciona numero de SALIDA: 7
 Selecciona numero de LLEGADA: 5

==================================================
 RUTA OPTIMA: [Suba] --> [Estacion Central]
==================================================
 Tiempo Total Estimado: 27.0 minutos

 Itinerario paso a paso:
  [1] Salir desde: Suba
  [2] Tomar Linea B hacia -> Polo (+8 min)
  [3] Tomar Linea B hacia -> Calle 72 (+4 min)
  [4] Tomar Linea A hacia -> Calle 26 (+10 min)
  [5] Tomar Linea A hacia -> Estacion Central (+5 min)
==================================================
```

---

## Estructura del Repositorio

* **`sistema_transporte.py`**: Código fuente principal en Python con la base de conocimiento, motor de reglas y algoritmo A*.
* **`guion_video_explicativo.md`**: Guion estructurado con tiempos y pautas para la presentación en video de la actividad.
* **`README.md`**: Documentación técnica del proyecto.
