# =============================================================
# ACTIVIDAD 4 - APRENDIZAJE NO SUPERVISADO
# Sistema Inteligente de Rutas - Transmilenio
# María José Navarrete Navarrete
# Corporación Universitaria Iberoamericana - 2026
# =============================================================
# OBJETIVO: Agrupar estaciones por características de uso
# usando K-Means (implementación manual, sin scikit-learn)
# =============================================================

import random
import math
import csv

# ──────────────────────────────────────────────
# 1. BASE DE CONOCIMIENTO
# ──────────────────────────────────────────────

base_conocimiento = {
    "Portal Norte":    [("Toberin", 3), ("Mazuren", 5)],
    "Toberin":         [("Portal Norte", 3), ("Cardio Infantil", 4)],
    "Mazuren":         [("Portal Norte", 5), ("Alcala", 4)],
    "Cardio Infantil": [("Toberin", 4), ("Calle 100", 5)],
    "Alcala":          [("Mazuren", 4), ("Calle 100", 3)],
    "Calle 100":       [("Cardio Infantil", 5), ("Alcala", 3), ("Heroes", 6)],
    "Heroes":          [("Calle 100", 6), ("Calle 45", 4), ("Calle 72", 5)],
    "Calle 72":        [("Heroes", 5), ("Flores", 4)],
    "Calle 45":        [("Heroes", 4), ("Marly", 3)],
    "Marly":           [("Calle 45", 3), ("Calle 26", 5)],
    "Flores":          [("Calle 72", 4), ("Calle 26", 6)],
    "Calle 26":        [("Marly", 5), ("Flores", 6), ("Paloquemao", 4)],
    "Paloquemao":      [("Calle 26", 4), ("La Sabana", 3)],
    "La Sabana":       [("Paloquemao", 3), ("Portal Sur", 8)],
    "Portal Sur":      [("La Sabana", 8)],
}

ESTACIONES = list(base_conocimiento.keys())

# ──────────────────────────────────────────────
# 2. GENERACIÓN DEL DATASET (características por estación)
# ──────────────────────────────────────────────

random.seed(7)

# Datos cualitativos de cada estación (simulados de forma realista)
TIPO_ZONA = {
    "Portal Norte": "residencial_norte", "Toberin": "residencial_norte",
    "Mazuren": "residencial_norte", "Cardio Infantil": "salud_educacion",
    "Alcala": "residencial_norte", "Calle 100": "comercial",
    "Heroes": "transbordo", "Calle 72": "comercial",
    "Calle 45": "educacion", "Marly": "salud_educacion",
    "Flores": "residencial_centro", "Calle 26": "transbordo",
    "Paloquemao": "comercial", "La Sabana": "transbordo",
    "Portal Sur": "residencial_sur",
}
TIPO_COD = {t: i for i, t in enumerate(set(TIPO_ZONA.values()))}

def generar_datos_estacion(estacion):
    idx = ESTACIONES.index(estacion)
    n_conexiones = len(base_conocimiento[estacion])
    tipo = TIPO_ZONA[estacion]

    # Pasajeros promedio por hora pico (depende del tipo y posición)
    base_pasajeros = {
        "transbordo": 1200, "comercial": 950, "salud_educacion": 700,
        "educacion": 680, "residencial_norte": 850,
        "residencial_centro": 600, "residencial_sur": 800
    }
    pasajeros_pico = base_pasajeros[tipo] + random.randint(-100, 100)
    pasajeros_valle = int(pasajeros_pico * random.uniform(0.3, 0.5))

    # Tiempo promedio de espera (minutos)
    espera_prom = round(random.uniform(2, 8) + (1 if tipo == "transbordo" else 0), 1)

    # Tiempo promedio de conexión con vecinos
    tiempos_vecinos = [t for _, t in base_conocimiento[estacion]]
    tiempo_medio_conexion = round(sum(tiempos_vecinos) / len(tiempos_vecinos), 2)

    # Índice de posición en la red (0 = Portal Norte, 14 = Portal Sur)
    posicion = idx / (len(ESTACIONES) - 1)  # normalizado 0..1

    # Incidentes reportados (por mes, estimado)
    incidentes = random.randint(0, 8)

    return {
        "estacion":            estacion,
        "n_conexiones":        n_conexiones,
        "tipo_zona":           tipo,
        "tipo_zona_cod":       TIPO_COD[tipo],
        "pasajeros_pico":      pasajeros_pico,
        "pasajeros_valle":     pasajeros_valle,
        "espera_prom_min":     espera_prom,
        "tiempo_medio_conex":  tiempo_medio_conexion,
        "posicion_red":        round(posicion, 3),
        "incidentes_mes":      incidentes,
    }

print("=" * 60)
print("  ACTIVIDAD 4 — APRENDIZAJE NO SUPERVISADO")
print("  Sistema de Rutas Transmilenio")
print("=" * 60)

print("\n[1/5] Generando dataset de estaciones...")
datos_estaciones = [generar_datos_estacion(e) for e in ESTACIONES]
print(f"      ✓ {len(datos_estaciones)} estaciones con características generadas")

# ──────────────────────────────────────────────
# 3. GUARDAR CSV
# ──────────────────────────────────────────────

CAMPOS = ["estacion","n_conexiones","tipo_zona","tipo_zona_cod",
          "pasajeros_pico","pasajeros_valle","espera_prom_min",
          "tiempo_medio_conex","posicion_red","incidentes_mes"]

csv_path = "dataset_no_supervisado.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=CAMPOS)
    writer.writeheader()
    writer.writerows(datos_estaciones)

print(f"      ✓ Dataset guardado en: {csv_path}")
print("\n      DATOS POR ESTACIÓN:")
print(f"      {'ESTACIÓN':<20} {'CONEXIONES':>10} {'PASAJ.PICO':>11} {'ESPERA':>7} {'POSICIÓN':>9}")
print("      " + "-" * 65)
for d in datos_estaciones:
    print(f"      {d['estacion']:<20} {d['n_conexiones']:>10} {d['pasajeros_pico']:>11} {d['espera_prom_min']:>7.1f} {d['posicion_red']:>9.3f}")

# ──────────────────────────────────────────────
# 4. NORMALIZACIÓN Y PREPARACIÓN DE FEATURES
# ──────────────────────────────────────────────

FEATURES_CLUSTER = ["n_conexiones", "pasajeros_pico", "espera_prom_min",
                    "tiempo_medio_conex", "posicion_red", "incidentes_mes"]

def normalizar(datos, features):
    mins = {f: min(d[f] for d in datos) for f in features}
    maxs = {f: max(d[f] for d in datos) for f in features}
    datos_norm = []
    for d in datos:
        vec = []
        for f in features:
            rango = maxs[f] - mins[f]
            vec.append((d[f] - mins[f]) / rango if rango != 0 else 0.0)
        datos_norm.append(vec)
    return datos_norm

X = normalizar(datos_estaciones, FEATURES_CLUSTER)

# ──────────────────────────────────────────────
# 5. K-MEANS MANUAL
# ──────────────────────────────────────────────

print("\n[2/5] Ejecutando K-Means (k=3 grupos)...")

def distancia_euclidea(a, b):
    return math.sqrt(sum((x - y)**2 for x, y in zip(a, b)))

def kmeans(X, k=3, max_iter=100, seed=42):
    random.seed(seed)
    # Inicializar centroides con puntos aleatorios distintos
    centroides = [X[i][:] for i in random.sample(range(len(X)), k)]
    asignaciones = [0] * len(X)

    for iteracion in range(max_iter):
        # Asignar cada punto al centroide más cercano
        nuevas_asig = []
        for punto in X:
            distancias = [distancia_euclidea(punto, c) for c in centroides]
            nuevas_asig.append(distancias.index(min(distancias)))

        # Verificar convergencia
        if nuevas_asig == asignaciones:
            print(f"      ✓ Convergió en iteración {iteracion + 1}")
            break
        asignaciones = nuevas_asig

        # Recalcular centroides
        nuevos_centroides = []
        for c in range(k):
            puntos_c = [X[j] for j in range(len(X)) if asignaciones[j] == c]
            if puntos_c:
                centroide = [sum(p[d] for p in puntos_c) / len(puntos_c)
                             for d in range(len(X[0]))]
                nuevos_centroides.append(centroide)
            else:
                nuevos_centroides.append(centroides[c])
        centroides = nuevos_centroides

    return asignaciones, centroides

K = 3
asignaciones, centroides = kmeans(X, k=K)

# ──────────────────────────────────────────────
# 6. CALCULAR INERCIA (métrica de calidad)
# ──────────────────────────────────────────────

def inercia(X, asig, centroides):
    return sum(distancia_euclidea(X[i], centroides[asig[i]])**2 for i in range(len(X)))

inercia_val = inercia(X, asignaciones, centroides)

# ──────────────────────────────────────────────
# 7. MÉTODO DEL CODO (evaluar k=2..6)
# ──────────────────────────────────────────────

print("\n[3/5] Método del codo (evaluando k=2..6)...")
print(f"\n      {'K':>3} │ {'INERCIA':>10}")
print("      ────┼────────────")
for k_eval in range(2, 7):
    asig_k, cent_k = kmeans(X, k=k_eval, seed=99)
    in_k = inercia(X, asig_k, cent_k)
    barra = "█" * int(in_k * 30)
    print(f"      {k_eval:>3} │ {in_k:>10.4f}  {barra}")

# ──────────────────────────────────────────────
# 8. RESULTADOS
# ──────────────────────────────────────────────

print(f"\n[4/5] Resultados del clustering (k={K}):")
print(f"\n      Inercia total: {inercia_val:.4f}")

ETIQUETAS = ["Grupo A - Estaciones de Alta Demanda",
             "Grupo B - Estaciones Intermedias",
             "Grupo C - Estaciones de Baja Densidad"]

# Ordenar grupos por pasajeros promedio (para etiquetar coherentemente)
prom_pasajeros_grupo = {}
for g in range(K):
    idx_g = [i for i, a in enumerate(asignaciones) if a == g]
    prom_pasajeros_grupo[g] = sum(datos_estaciones[i]['pasajeros_pico'] for i in idx_g) / max(len(idx_g), 1)

orden = sorted(range(K), key=lambda g: -prom_pasajeros_grupo[g])
mapa_etiqueta = {orden[i]: i for i in range(K)}

print()
for g in range(K):
    idx_g = [i for i, a in enumerate(asignaciones) if a == g]
    etiqueta = ETIQUETAS[mapa_etiqueta[g]]
    print(f"\n      🏷️  {etiqueta}:")
    print(f"      {'─'*55}")
    for i in idx_g:
        d = datos_estaciones[i]
        print(f"      • {d['estacion']:<20} | Pasaj.pico: {d['pasajeros_pico']:>4} "
              f"| Conexiones: {d['n_conexiones']} | Zona: {d['tipo_zona']}")

# ──────────────────────────────────────────────
# 9. GUARDAR RESULTADOS CON CLUSTER
# ──────────────────────────────────────────────

print("\n[5/5] Guardando resultados...")
resultado_path = "resultados_clustering.csv"
with open(resultado_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["estacion", "cluster", "etiqueta_cluster",
                     "n_conexiones", "pasajeros_pico", "tipo_zona", "posicion_red"])
    for i, d in enumerate(datos_estaciones):
        g = asignaciones[i]
        writer.writerow([d["estacion"], g, ETIQUETAS[mapa_etiqueta[g]],
                         d["n_conexiones"], d["pasajeros_pico"],
                         d["tipo_zona"], d["posicion_red"]])

print(f"      ✓ Resultados guardados en: {resultado_path}")

print("\n" + "=" * 60)
print("  ✅ Actividad 4 completada exitosamente")
print("=" * 60)
