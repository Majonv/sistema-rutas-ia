# =============================================================
# ACTIVIDAD 3 - APRENDIZAJE SUPERVISADO
# Sistema Inteligente de Rutas - Transmilenio
# María José Navarrete Navarrete
# Corporación Universitaria Iberoamericana - 2026
# =============================================================
# OBJETIVO: Predecir el tiempo de viaje entre estaciones
# usando un modelo de Regresión (Random Forest Regressor)
# =============================================================

import random
import math
import heapq

# ──────────────────────────────────────────────
# 1. BASE DE CONOCIMIENTO (del proyecto anterior)
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
ESTACION_IDX = {e: i for i, e in enumerate(ESTACIONES)}

# ──────────────────────────────────────────────
# 2. ALGORITMO A* (para calcular tiempos reales)
# ──────────────────────────────────────────────

def heuristica(estacion, destino):
    return abs(ESTACION_IDX[destino] - ESTACION_IDX[estacion]) * 3

def buscar_ruta(inicio, fin):
    if inicio == fin:
        return 0, 0
    cola = []
    heapq.heappush(cola, (heuristica(inicio, fin), 0, inicio, [inicio]))
    visitados = {}
    while cola:
        f, g, actual, ruta = heapq.heappop(cola)
        if actual == fin:
            return g, len(ruta) - 1
        if actual in visitados and visitados[actual] <= g:
            continue
        visitados[actual] = g
        for vecino, costo in base_conocimiento[actual]:
            if vecino not in visitados:
                nuevo_g = g + costo
                heapq.heappush(cola, (nuevo_g + heuristica(vecino, fin), nuevo_g, vecino, ruta + [vecino]))
    return None, None

# ──────────────────────────────────────────────
# 3. GENERACIÓN DEL DATASET SINTÉTICO
# ──────────────────────────────────────────────

random.seed(42)

HORARIOS = ["Mañana (6-9h)", "Valle (9-12h)", "Tarde (12-16h)", "Pico tarde (16-20h)", "Noche (20-23h)"]
HORARIO_FACTOR = {"Mañana (6-9h)": 1.30, "Valle (9-12h)": 1.00, "Tarde (12-16h)": 1.10,
                  "Pico tarde (16-20h)": 1.35, "Noche (20-23h)": 0.90}
HORARIO_PASAJEROS = {"Mañana (6-9h)": (800, 1200), "Valle (9-12h)": (300, 600),
                     "Tarde (12-16h)": (500, 800), "Pico tarde (16-20h)": (900, 1300),
                     "Noche (20-23h)": (100, 350)}

def generar_dataset(n=300):
    datos = []
    pares = [(o, d) for o in ESTACIONES for d in ESTACIONES if o != d]
    for _ in range(n):
        origen, destino = random.choice(pares)
        tiempo_base, paradas = buscar_ruta(origen, destino)
        if tiempo_base is None:
            continue
        horario = random.choice(HORARIOS)
        factor = HORARIO_FACTOR[horario]
        min_p, max_p = HORARIO_PASAJEROS[horario]
        pasajeros = random.randint(min_p, max_p)
        lluvia = random.choice([0, 1])
        factor_lluvia = 1.15 if lluvia else 1.0
        ruido = random.uniform(-1.5, 1.5)
        tiempo_real = round(tiempo_base * factor * factor_lluvia + ruido, 1)
        tiempo_real = max(tiempo_real, tiempo_base * 0.8)

        datos.append({
            "origen":          origen,
            "destino":         destino,
            "idx_origen":      ESTACION_IDX[origen],
            "idx_destino":     ESTACION_IDX[destino],
            "distancia_idx":   abs(ESTACION_IDX[destino] - ESTACION_IDX[origen]),
            "paradas":         paradas,
            "horario":         horario,
            "horario_cod":     HORARIOS.index(horario),
            "pasajeros":       pasajeros,
            "lluvia":          lluvia,
            "tiempo_base":     tiempo_base,
            "tiempo_real_min": tiempo_real,
        })
    return datos

print("=" * 60)
print("  ACTIVIDAD 3 — APRENDIZAJE SUPERVISADO")
print("  Sistema de Rutas Transmilenio")
print("=" * 60)

print("\n[1/5] Generando dataset sintético...")
dataset = generar_dataset(300)
print(f"      ✓ {len(dataset)} registros generados")

# ──────────────────────────────────────────────
# 4. GUARDAR DATASET EN CSV
# ──────────────────────────────────────────────

import csv, os

CAMPOS = ["origen","destino","idx_origen","idx_destino","distancia_idx",
          "paradas","horario","horario_cod","pasajeros","lluvia",
          "tiempo_base","tiempo_real_min"]

csv_path = "dataset_supervisado.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=CAMPOS)
    writer.writeheader()
    writer.writerows(dataset)

print(f"\n[2/5] Dataset guardado en: {csv_path}")
print("\n      Primeras 5 filas:")
print(f"      {'ORIGEN':<18} {'DESTINO':<18} {'PARADAS':>7} {'HORARIO':<22} {'PASAJ':>6} {'LLUVIA':>6} {'T.BASE':>7} {'T.REAL':>7}")
print("      " + "-" * 80)
for row in dataset[:5]:
    print(f"      {row['origen']:<18} {row['destino']:<18} {row['paradas']:>7} {row['horario']:<22} {row['pasajeros']:>6} {row['lluvia']:>6} {row['tiempo_base']:>7} {row['tiempo_real_min']:>7}")

# ──────────────────────────────────────────────
# 5. IMPLEMENTACIÓN MANUAL DE RANDOM FOREST
#    (sin scikit-learn, solo librería estándar)
# ──────────────────────────────────────────────

print("\n[3/5] Entrenando modelo (Random Forest Manual)...")

FEATURES = ["idx_origen", "idx_destino", "distancia_idx", "paradas",
            "horario_cod", "pasajeros", "lluvia", "tiempo_base"]
TARGET   = "tiempo_real_min"

def get_X_y(datos):
    X = [[d[f] for f in FEATURES] for d in datos]
    y = [d[TARGET] for d in datos]
    return X, y

# Dividir 80% train / 20% test
random.seed(0)
indices = list(range(len(dataset)))
random.shuffle(indices)
corte = int(len(indices) * 0.8)
train_data = [dataset[i] for i in indices[:corte]]
test_data  = [dataset[i] for i in indices[corte:]]

X_train, y_train = get_X_y(train_data)
X_test,  y_test  = get_X_y(test_data)

# ── Árbol de decisión simple (CART manual) ──

class NodoArbol:
    def __init__(self):
        self.feat_idx = None
        self.umbral   = None
        self.izq      = None
        self.der      = None
        self.valor    = None  # hoja

def varianza(vals):
    if not vals: return 0
    m = sum(vals) / len(vals)
    return sum((v - m) ** 2 for v in vals) / len(vals)

def mejor_split(X, y, n_features=None):
    n, m = len(X), len(X[0])
    feat_indices = list(range(m))
    if n_features:
        feat_indices = random.sample(feat_indices, min(n_features, m))
    mejor_gain, mejor_fi, mejor_umb = -1, None, None
    var_total = varianza(y)
    for fi in feat_indices:
        vals = sorted(set(x[fi] for x in X))
        for i in range(len(vals) - 1):
            umb = (vals[i] + vals[i+1]) / 2
            y_izq = [y[j] for j in range(n) if X[j][fi] <= umb]
            y_der = [y[j] for j in range(n) if X[j][fi] >  umb]
            if not y_izq or not y_der:
                continue
            gain = var_total - (len(y_izq)/n * varianza(y_izq) + len(y_der)/n * varianza(y_der))
            if gain > mejor_gain:
                mejor_gain, mejor_fi, mejor_umb = gain, fi, umb
    return mejor_fi, mejor_umb

def construir_arbol(X, y, profundidad=0, max_prof=5, min_muestras=5, n_features=None):
    nodo = NodoArbol()
    if len(y) <= min_muestras or profundidad >= max_prof:
        nodo.valor = sum(y) / len(y)
        return nodo
    fi, umb = mejor_split(X, y, n_features)
    if fi is None:
        nodo.valor = sum(y) / len(y)
        return nodo
    nodo.feat_idx = fi
    nodo.umbral   = umb
    mask_izq = [X[j][fi] <= umb for j in range(len(X))]
    X_izq = [X[j] for j in range(len(X)) if mask_izq[j]]
    y_izq = [y[j] for j in range(len(y)) if mask_izq[j]]
    X_der = [X[j] for j in range(len(X)) if not mask_izq[j]]
    y_der = [y[j] for j in range(len(y)) if not mask_izq[j]]
    nodo.izq = construir_arbol(X_izq, y_izq, profundidad+1, max_prof, min_muestras, n_features)
    nodo.der = construir_arbol(X_der, y_der, profundidad+1, max_prof, min_muestras, n_features)
    return nodo

def predecir_arbol(nodo, x):
    if nodo.valor is not None:
        return nodo.valor
    if x[nodo.feat_idx] <= nodo.umbral:
        return predecir_arbol(nodo.izq, x)
    return predecir_arbol(nodo.der, x)

# ── Random Forest ──

N_ARBOLES = 15

def entrenar_forest(X, y, n_arboles=N_ARBOLES):
    arboles = []
    n = len(X)
    for _ in range(n_arboles):
        # Bootstrap
        idx = [random.randint(0, n-1) for _ in range(n)]
        Xb = [X[i] for i in idx]
        yb = [y[i] for i in idx]
        arbol = construir_arbol(Xb, yb, max_prof=6, min_muestras=4,
                                n_features=int(math.sqrt(len(FEATURES))))
        arboles.append(arbol)
    return arboles

def predecir_forest(arboles, X):
    return [sum(predecir_arbol(a, x) for a in arboles) / len(arboles) for x in X]

arboles = entrenar_forest(X_train, y_train)
print(f"      ✓ {N_ARBOLES} árboles entrenados")

# ──────────────────────────────────────────────
# 6. EVALUACIÓN
# ──────────────────────────────────────────────

print("\n[4/5] Evaluando el modelo...")

y_pred = predecir_forest(arboles, X_test)

def mae(real, pred):
    return sum(abs(r - p) for r, p in zip(real, pred)) / len(real)

def rmse(real, pred):
    return math.sqrt(sum((r - p)**2 for r, p in zip(real, pred)) / len(real))

def r2(real, pred):
    media = sum(real) / len(real)
    ss_tot = sum((r - media)**2 for r in real)
    ss_res = sum((r - p)**2 for r, p in zip(real, pred))
    return 1 - ss_res / ss_tot if ss_tot != 0 else 0

mae_val  = mae(y_test, y_pred)
rmse_val = rmse(y_test, y_pred)
r2_val   = r2(y_test, y_pred)

print(f"\n      📊 MÉTRICAS DE EVALUACIÓN (conjunto de prueba):")
print(f"      ─────────────────────────────────────────")
print(f"      MAE  (Error Absoluto Medio):  {mae_val:.2f} minutos")
print(f"      RMSE (Raíz Error Cuadrático): {rmse_val:.2f} minutos")
print(f"      R²   (Coef. Determinación):   {r2_val:.4f}")

# ──────────────────────────────────────────────
# 7. PREDICCIONES DE EJEMPLO
# ──────────────────────────────────────────────

print("\n[5/5] Predicciones de ejemplo:")
print(f"\n      {'ORIGEN':<18} {'DESTINO':<18} {'HORARIO':<22} {'LLUVIA':>6} {'REAL':>6} {'PRED':>6} {'ERROR':>6}")
print("      " + "-" * 90)

for row, real, pred in zip(test_data[:8], y_test[:8], y_pred[:8]):
    lluvia_txt = "Sí" if row['lluvia'] else "No"
    error = abs(real - pred)
    print(f"      {row['origen']:<18} {row['destino']:<18} {row['horario']:<22} {lluvia_txt:>6} {real:>6.1f} {pred:>6.1f} {error:>6.1f}")

print("\n" + "=" * 60)
print("  ✅ Actividad 3 completada exitosamente")
print("=" * 60)
