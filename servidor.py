"""
servidor.py — Servidor central Stickers App
Corre este archivo PRIMERO antes de abrir la app.
"""
from flask import Flask, request, jsonify
import json, os, math, itertools
from datetime import datetime

app = Flask(__name__)
DB_FILE = "usuarios_db.json"

# ── BASE DE DATOS ────────────────────────────────────────────────────
def cargar_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {}

def guardar_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def distancia_km(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1-lat2)**2 + (lon1-lon2)**2) * 111

# ── ENDPOINTS ────────────────────────────────────────────────────────

@app.route("/registrar", methods=["POST"])
def registrar():
    """Registra o actualiza un usuario con su álbum."""
    data = request.json
    db   = cargar_db()
    uid  = data["usuario_id"]
    db[uid] = {
        "nombre":    data["nombre"],
        "repetidas": data["repetidas"],
        "faltantes": data["faltantes"],
        "lat":       data["lat"],
        "lon":       data["lon"],
        "ultima_vez": datetime.now().isoformat(),
    }
    guardar_db(db)
    return jsonify({"ok": True, "mensaje": f"Usuario {data['nombre']} registrado"})


@app.route("/buscar_grupos", methods=["POST"])
def buscar_grupos():
    """
    Busca grupos de 2-5 usuarios cercanos que puedan hacer
    intercambio circular de estampas.
    """
    data        = request.json
    mi_id       = data["usuario_id"]
    radio_km    = data.get("radio_km", 5.0)
    max_grupo   = data.get("max_grupo", 5)

    db = cargar_db()
    if mi_id not in db:
        return jsonify({"ok": False, "grupos": [], "mensaje": "Usuario no registrado"})

    yo = db[mi_id]

    # 1. Filtrar usuarios cercanos
    cercanos = {}
    for uid, u in db.items():
        if uid == mi_id: continue
        dist = distancia_km(yo["lat"], yo["lon"], u["lat"], u["lon"])
        if dist <= radio_km:
            cercanos[uid] = {**u, "dist_km": round(dist, 2)}

    if not cercanos:
        return jsonify({"ok": True, "grupos": [], "mensaje": "No hay usuarios cercanos"})

    # Incluimos al usuario actual en el pool
    pool = {mi_id: yo, **cercanos}

    # 2. Buscar grupos con intercambio circular
    grupos_validos = []

    for tam in range(2, min(max_grupo+1, len(pool)+1)):
        for combo in itertools.combinations(pool.keys(), tam):
            if mi_id not in combo:
                continue  # Solo grupos que incluyan al usuario actual

            grupo_ids = list(combo)
            miembros  = {uid: pool[uid] for uid in grupo_ids}

            # Verificar que hay intercambio circular útil
            # Para cada miembro, ¿alguien del grupo tiene lo que necesita?
            beneficios = {}
            for uid_a in grupo_ids:
                fal_a = set(miembros[uid_a]["faltantes"])
                recibe = []
                for uid_b in grupo_ids:
                    if uid_b == uid_a: continue
                    rep_b = set(miembros[uid_b]["repetidas"])
                    puede_dar = sorted(rep_b & fal_a)
                    if puede_dar:
                        recibe.append({"de": miembros[uid_b]["nombre"], "estampas": puede_dar})
                if recibe:
                    beneficios[uid_a] = recibe

            # Grupo válido si AL MENOS la mitad de miembros se beneficia
            min_beneficiados = max(2, len(grupo_ids) // 2)
            if len(beneficios) >= min_beneficiados:
                total_estampas = sum(
                    len(e["estampas"])
                    for b in beneficios.values()
                    for e in b
                )
                grupos_validos.append({
                    "miembros": [
                        {
                            "id":       uid,
                            "nombre":   miembros[uid]["nombre"],
                            "lat":      miembros[uid]["lat"],
                            "lon":      miembros[uid]["lon"],
                            "dist_km":  miembros[uid].get("dist_km", 0),
                            "recibe":   beneficios.get(uid, []),
                        }
                        for uid in grupo_ids
                    ],
                    "total_estampas": total_estampas,
                    "tamaño": len(grupo_ids),
                })

    # Ordenar por total de estampas intercambiables
    grupos_validos.sort(key=lambda g: -g["total_estampas"])

    return jsonify({
        "ok":     True,
        "grupos": grupos_validos[:10],  # máx 10 grupos
        "mensaje": f"Se encontraron {len(grupos_validos)} grupos posibles"
    })


@app.route("/usuarios_cercanos", methods=["POST"])
def usuarios_cercanos():
    """Lista usuarios cercanos registrados."""
    data     = request.json
    radio_km = data.get("radio_km", 5.0)
    lat, lon = data["lat"], data["lon"]
    db       = cargar_db()
    resultado = []
    for uid, u in db.items():
        dist = distancia_km(lat, lon, u["lat"], u["lon"])
        if dist <= radio_km:
            resultado.append({
                "id":     uid,
                "nombre": u["nombre"],
                "dist_km": round(dist, 2),
                "repetidas_count": len(u["repetidas"]),
                "faltantes_count": len(u["faltantes"]),
            })
    resultado.sort(key=lambda x: x["dist_km"])
    return jsonify({"ok": True, "usuarios": resultado})


@app.route("/ping")
def ping():
    return jsonify({"ok": True, "mensaje": "Servidor Stickers App activo"})


if __name__ == "__main__":
    print("=" * 50)
    print("  🏟️  Servidor Stickers App iniciando...")
    print("  📡  Escuchando en http://localhost:5000")
    print("  ⚠️   Deja esta ventana abierta")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False)
