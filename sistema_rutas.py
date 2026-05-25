# SISTEMA INTELIGENTE DE RUTAS - TRANSPORTE MASIVO

import heapq

# --- BASE DE CONOCIMIENTO ---

base_conocimiento = {
    "Portal Norte": [("Toberin", 3), ("Mazuren", 5)],
    "Toberin":      [("Portal Norte", 3), ("Cardio Infantil", 4)],
    "Mazuren":      [("Portal Norte", 5), ("Alcala", 4)],
    "Cardio Infantil": [("Toberin", 4), ("Calle 100", 5)],
    "Alcala":       [("Mazuren", 4), ("Calle 100", 3)],
    "Calle 100":    [("Cardio Infantil", 5), ("Alcala", 3), ("Heroes", 6)],
    "Heroes":       [("Calle 100", 6), ("Calle 45", 4), ("Calle 72", 5)],
    "Calle 72":     [("Heroes", 5), ("Flores", 4)],
    "Calle 45":     [("Heroes", 4), ("Marly", 3)],
    "Marly":        [("Calle 45", 3), ("Calle 26", 5)],
    "Flores":       [("Calle 72", 4), ("Calle 26", 6)],
    "Calle 26":     [("Marly", 5), ("Flores", 6), ("Paloquemao", 4)],
    "Paloquemao":   [("Calle 26", 4), ("La Sabana", 3)],
    "La Sabana":    [("Paloquemao", 3), ("Portal Sur", 8)],
    "Portal Sur":   [("La Sabana", 8)]
}

# --- REGLAS LÓGICAS ---

def regla_estacion_valida(estacion):
    return estacion in base_conocimiento

def regla_conexion_existe(origen, destino):
    if not regla_estacion_valida(origen):
        return False
    vecinos = [v for v, _ in base_conocimiento[origen]]
    return destino in vecinos

# --- HEURÍSTICA ---

def heuristica(estacion, destino, grafo):
    estaciones = list(grafo.keys())
    try:
        idx_actual = estaciones.index(estacion)
        idx_destino = estaciones.index(destino)
        return abs(idx_destino - idx_actual) * 3
    except ValueError:
        return 0

# --- ALGORITMO A* ---

def buscar_ruta_optima(inicio, fin):
    if not regla_estacion_valida(inicio):
        print(f"ERROR: La estación '{inicio}' no existe en la base de conocimiento.")
        return None, None
    if not regla_estacion_valida(fin):
        print(f"ERROR: La estación '{fin}' no existe en la base de conocimiento.")
        return None, None
    if inicio == fin:
        return [inicio], 0

    cola = []
    heapq.heappush(cola, (heuristica(inicio, fin, base_conocimiento), 0, inicio, [inicio]))
    visitados = {}

    while cola:
        f, g, actual, ruta = heapq.heappop(cola)
        if actual == fin:
            return ruta, g
        if actual in visitados and visitados[actual] <= g:
            continue
        visitados[actual] = g
        for vecino, costo in base_conocimiento[actual]:
            if vecino not in visitados:
                nuevo_g = g + costo
                nuevo_f = nuevo_g + heuristica(vecino, fin, base_conocimiento)
                heapq.heappush(cola, (nuevo_f, nuevo_g, vecino, ruta + [vecino]))

    return None, None

# --- INTERFAZ DE USUARIO ---

def mostrar_estaciones():
    print("\n📍 ESTACIONES DISPONIBLES:")
    print("-" * 35)
    for i, estacion in enumerate(base_conocimiento.keys(), 1):
        print(f"  {i:2}. {estacion}")
    print("-" * 35)

def mostrar_resultado(ruta, tiempo):
    if ruta is None:
        print("\n❌ No se encontró ruta entre las estaciones indicadas.")
        return
    print("\n✅ RUTA ÓPTIMA ENCONTRADA:")
    print("-" * 35)
    for i, estacion in enumerate(ruta):
        if i == 0:
            print(f"  🟢 INICIO: {estacion}")
        elif i == len(ruta) - 1:
            print(f"  🔴 DESTINO: {estacion}")
        else:
            print(f"  🔵 Parada {i}: {estacion}")
    print("-" * 35)
    print(f"  📊 Total de paradas: {len(ruta) - 1}")
    print(f"  ⏱️  Tiempo estimado: {tiempo} minutos")
    print("-" * 35)

def main():
    print("=" * 45)
    print("  🚇 SISTEMA DE RUTAS - TRANSPORTE MASIVO")
    print("=" * 45)

    mostrar_estaciones()

    print("\nIngresa las estaciones:")
    inicio = input("  ▶ Estación de ORIGEN:  ").strip()
    fin    = input("  ▶ Estación de DESTINO: ").strip()

    print(f"\n🔍 Buscando ruta de '{inicio}' a '{fin}'...")
    ruta, tiempo = buscar_ruta_optima(inicio, fin)
    mostrar_resultado(ruta, tiempo)

    print("\n" + "=" * 45)
    print("  EJEMPLO: Portal Norte → Portal Sur")
    print("=" * 45)
    ruta2, tiempo2 = buscar_ruta_optima("Portal Norte", "Portal Sur")
    mostrar_resultado(ruta2, tiempo2)

if __name__ == "__main__":
    main()
