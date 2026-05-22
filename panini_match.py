import os, json, random, threading, subprocess, uuid
os.environ["PYTHONHTTPSVERIFY"] = "0"

import flet as ft
import qrcode
import cv2
import requests
import threading as _th



# ── NOTIFICACIONES WINDOWS (Toast) ───────────────────────────────
def notif_windows(titulo, mensaje, icono="info"):
    """Muestra notificación del sistema Windows."""
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(
            titulo, mensaje,
            duration=5, threaded=True,
            icon_path=None
        )
    except ImportError:
        # Fallback: usar subprocess con PowerShell
        try:
            import subprocess
            ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.BalloonTipIcon = 'Info'
$notify.BalloonTipTitle = '{titulo}'
$notify.BalloonTipText = '{mensaje}'
$notify.Visible = $True
$notify.ShowBalloonTip(5000)
Start-Sleep -Seconds 6
$notify.Dispose()
"""
            subprocess.Popen(
                ["powershell", "-WindowStyle", "Hidden", "-Command", ps_script],
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        except Exception: pass
    except Exception: pass

# ── MERCADO DE ESTAMPAS ───────────────────────────────────────────
ARCHIVO_MERCADO = "mercado_db.json"

def cargar_mercado():
    if os.path.exists(ARCHIVO_MERCADO):
        try:
            with open(ARCHIVO_MERCADO,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {}

def guardar_mercado(data):
    try:
        with open(ARCHIVO_MERCADO,"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
        return True
    except: return False

# ── REPUTACIÓN, EVENTOS Y NOTIFICACIONES ─────────────────────────
ARCHIVO_REPUTACION = "reputacion_db.json"
ARCHIVO_EVENTOS    = "eventos_db.json"
ARCHIVO_NOTIF      = "notificaciones.json"

def cargar_json(archivo):
    if os.path.exists(archivo):
        try:
            with open(archivo,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {}

def guardar_json(archivo, data):
    try:
        with open(archivo,"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
        return True
    except: return False

def agregar_notificacion(mensaje, tipo="info"):
    notifs = cargar_json(ARCHIVO_NOTIF)
    if "lista" not in notifs: notifs["lista"] = []
    from datetime import datetime
    notifs["lista"].insert(0, {
        "msg": mensaje,
        "tipo": tipo,
        "fecha": datetime.now().strftime("%d/%m %H:%M"),
        "leida": False,
    })
    notifs["lista"] = notifs["lista"][:50]  # max 50
    guardar_json(ARCHIVO_NOTIF, notifs)
    # Mostrar notificación del sistema Windows
    titulos = {
        "intercambio": "🔄 Stickers — Intercambio",
        "evento":      "📅 Stickers — Evento",
        "reputacion":  "⭐ Stickers — Reputación",
        "grupo":       "👥 Stickers — Grupos",
        "mercado":     "🛒 Stickers — Mercado",
        "info":        "🔔 Stickers",
    }
    titulo = titulos.get(tipo, "🔔 Stickers")
    notif_windows(titulo, mensaje[:100])

def contar_no_leidas():
    notifs = cargar_json(ARCHIVO_NOTIF)
    return sum(1 for n in notifs.get("lista",[]) if not n.get("leida",False))

# ── ESTAMPAS ESPECIALES MUNDIAL 2026 ────────────────────────────────
ESPECIALES = {
    "ICONOS": {
        "nombre": "Íconos Mundiales ⭐",
        "color": "amber",
        "descripcion": "Las estampas más valiosas del álbum",
        "estampas": [
            {"id":"ICON1", "jugador":"Lionel Messi", "pais":"Argentina 🇦🇷", "tipo":"Foil Dorado"},
            {"id":"ICON2", "jugador":"Cristiano Ronaldo", "pais":"Portugal 🇵🇹", "tipo":"Foil Dorado"},
            {"id":"ICON3", "jugador":"Lamine Yamal", "pais":"España 🇪🇸", "tipo":"Foil Dorado"},
            {"id":"ICON4", "jugador":"Kylian Mbappé", "pais":"Francia 🇫🇷", "tipo":"Foil Dorado"},
            {"id":"ICON5", "jugador":"Erling Haaland", "pais":"Noruega 🇳🇴", "tipo":"Foil Dorado"},
            {"id":"ICON6", "jugador":"Vinicius Jr.", "pais":"Brasil 🇧🇷", "tipo":"Foil Dorado"},
            {"id":"ICON7", "jugador":"Jude Bellingham", "pais":"Inglaterra 🏴󠁧󠁢󠁥󠁮󠁧󠁿", "tipo":"Foil Dorado"},
            {"id":"ICON8", "jugador":"Harry Kane", "pais":"Inglaterra 🏴󠁧󠁢󠁥󠁮󠁧󠁿", "tipo":"Foil Dorado"},
            {"id":"ICON9", "jugador":"Pedri", "pais":"España 🇪🇸", "tipo":"Foil Dorado"},
            {"id":"ICON10", "jugador":"Rodri", "pais":"España 🇪🇸", "tipo":"Foil Dorado"},
            {"id":"ICON11", "jugador":"Lautaro Martínez", "pais":"Argentina 🇦🇷", "tipo":"Foil Dorado"},
            {"id":"ICON12", "jugador":"Christian Pulisic", "pais":"Estados Unidos 🇺🇸", "tipo":"Foil Dorado"},
        ]
    },
    "MUSEO": {
        "nombre": "Campeones Históricos 🏆",
        "color": "purple",
        "descripcion": "Campeones históricos del mundo (foil)",
        "estampas": [
            {"id":"FWC9",  "jugador":"Italia 1934", "pais":"Campeón Mundial", "tipo":"Foil Histórico"},
            {"id":"FWC10", "jugador":"Uruguay 1950", "pais":"Campeón Mundial", "tipo":"Foil Histórico"},
            {"id":"FWC11", "jugador":"Alemania 1954", "pais":"Campeón Mundial", "tipo":"Foil Histórico"},
            {"id":"FWC12", "jugador":"Brasil 1962", "pais":"Campeón Mundial", "tipo":"Foil Histórico"},
            {"id":"FWC13", "jugador":"Alemania 1974", "pais":"Campeón Mundial", "tipo":"Foil Histórico"},
            {"id":"FWC14", "jugador":"Argentina 1986", "pais":"Campeón Mundial", "tipo":"Foil Histórico"},
            {"id":"FWC15", "jugador":"Brasil 1994", "pais":"Campeón Mundial", "tipo":"Foil Histórico"},
            {"id":"FWC16", "jugador":"Brasil 2002", "pais":"Campeón Mundial", "tipo":"Foil Histórico"},
            {"id":"FWC17", "jugador":"Italia 2006", "pais":"Campeón Mundial", "tipo":"Foil Histórico"},
            {"id":"FWC18", "jugador":"Alemania 2014", "pais":"Campeón Mundial", "tipo":"Foil Histórico"},
            {"id":"FWC19", "jugador":"Argentina 2022", "pais":"Campeón Mundial", "tipo":"Foil Histórico"},
        ]
    },
    "PARALLELS": {
        "nombre": "Parallels Exclusivos 🎨",
        "color": "blue",
        "descripcion": "Versiones de color exclusivas de Norteamérica",
        "estampas": [
            {"id":"PAR-MESSI-BLUE",   "jugador":"Messi Azul",         "pais":"Argentina 🇦🇷",      "tipo":"Parallel Azul"},
            {"id":"PAR-MESSI-RED",    "jugador":"Messi Rojo",          "pais":"Argentina 🇦🇷",      "tipo":"Parallel Rojo"},
            {"id":"PAR-MESSI-PURPLE", "jugador":"Messi Púrpura",       "pais":"Argentina 🇦🇷",      "tipo":"Parallel Púrpura"},
            {"id":"PAR-MESSI-GREEN",  "jugador":"Messi Verde",         "pais":"Argentina 🇦🇷",      "tipo":"Parallel Verde"},
            {"id":"PAR-CR7-BLUE",     "jugador":"Ronaldo Azul",        "pais":"Portugal 🇵🇹",       "tipo":"Parallel Azul"},
            {"id":"PAR-CR7-RED",      "jugador":"Ronaldo Rojo",        "pais":"Portugal 🇵🇹",       "tipo":"Parallel Rojo"},
            {"id":"PAR-CR7-PURPLE",   "jugador":"Ronaldo Púrpura",     "pais":"Portugal 🇵🇹",       "tipo":"Parallel Púrpura"},
            {"id":"PAR-YML-BLUE",     "jugador":"Yamal Azul",          "pais":"España 🇪🇸",         "tipo":"Parallel Azul"},
            {"id":"PAR-YML-RED",      "jugador":"Yamal Rojo",          "pais":"España 🇪🇸",         "tipo":"Parallel Rojo"},
            {"id":"PAR-MBP-BLUE",     "jugador":"Mbappé Azul",         "pais":"Francia 🇫🇷",        "tipo":"Parallel Azul"},
            {"id":"PAR-MBP-RED",      "jugador":"Mbappé Rojo",         "pais":"Francia 🇫🇷",        "tipo":"Parallel Rojo"},
            {"id":"PAR-VIN-BLUE",     "jugador":"Vinicius Azul",       "pais":"Brasil 🇧🇷",         "tipo":"Parallel Azul"},
            {"id":"PAR-HAA-BLUE",     "jugador":"Haaland Azul",        "pais":"Noruega 🇳🇴",        "tipo":"Parallel Azul"},
            {"id":"PAR-BEL-BLUE",     "jugador":"Bellingham Azul",     "pais":"Inglaterra 🏴󠁧󠁢󠁥󠁮󠁧󠁿",   "tipo":"Parallel Azul"},
            {"id":"PAR-MESSI-BLACK",  "jugador":"Messi Negro 1/1",     "pais":"Argentina 🇦🇷",      "tipo":"⚫ Black 1-of-1"},
            {"id":"PAR-CR7-BLACK",    "jugador":"Ronaldo Negro 1/1",   "pais":"Portugal 🇵🇹",       "tipo":"⚫ Black 1-of-1"},
        ]
    },
    "COCACOLA": {
        "nombre": "Exclusivas Especiales 🥤",
        "color": "red",
        "descripcion": "Solo en tapas de botellas Especial",
        "estampas": [
            {"id":"CC1",  "jugador":"Lamine Yamal",       "pais":"España 🇪🇸",         "tipo":"Edición Especial"},
            {"id":"CC2",  "jugador":"Harry Kane",          "pais":"Inglaterra 🏴󠁧󠁢󠁥󠁮󠁧󠁿",   "tipo":"Edición Especial"},
            {"id":"CC3",  "jugador":"Joshua Kimmich",      "pais":"Alemania 🇩🇪",       "tipo":"Edición Especial"},
            {"id":"CC4",  "jugador":"Lautaro Martínez",    "pais":"Argentina 🇦🇷",      "tipo":"Edición Especial"},
            {"id":"CC5",  "jugador":"Jefferson Lerma",     "pais":"Colombia 🇨🇴",       "tipo":"Edición Especial"},
            {"id":"CC6",  "jugador":"Vinicius Jr.",         "pais":"Brasil 🇧🇷",         "tipo":"Edición Especial"},
            {"id":"CC7",  "jugador":"Pedri",               "pais":"España 🇪🇸",         "tipo":"Edición Especial"},
            {"id":"CC8",  "jugador":"Jude Bellingham",     "pais":"Inglaterra 🏴󠁧󠁢󠁥󠁮󠁧󠁿",   "tipo":"Edición Especial"},
            {"id":"CC9",  "jugador":"Erling Haaland",      "pais":"Noruega 🇳🇴",        "tipo":"Edición Especial"},
            {"id":"CC10", "jugador":"Christian Pulisic",   "pais":"Estados Unidos 🇺🇸", "tipo":"Edición Especial"},
            {"id":"CC11", "jugador":"Lionel Messi",        "pais":"Argentina 🇦🇷",      "tipo":"Edición Especial"},
            {"id":"CC12", "jugador":"Cristiano Ronaldo",   "pais":"Portugal 🇵🇹",       "tipo":"Edición Especial"},
        ]
    },
    "CRUMPLE": {
        "nombre": "Edición Limitada ✨",
        "color": "green",
        "descripcion": "Exclusivos online de Stickers y Amazon",
        "estampas": [
            {"id":"GC-MESSI",   "jugador":"Messi Edición Oro",      "pais":"Argentina 🇦🇷",    "tipo":"Edición Oro"},
            {"id":"GC-CR7",     "jugador":"Ronaldo Edición Oro",    "pais":"Portugal 🇵🇹",     "tipo":"Edición Oro"},
            {"id":"GC-YML",     "jugador":"Yamal Edición Oro",      "pais":"España 🇪🇸",       "tipo":"Edición Oro"},
            {"id":"GC-MBP",     "jugador":"Mbappé Edición Oro",     "pais":"Francia 🇫🇷",      "tipo":"Edición Oro"},
            {"id":"GC-VIN",     "jugador":"Vinicius Edición Oro",   "pais":"Brasil 🇧🇷",       "tipo":"Edición Oro"},
            {"id":"GC-HAA",     "jugador":"Haaland Edición Oro",    "pais":"Noruega 🇳🇴",      "tipo":"Edición Oro"},
            {"id":"OC-MESSI",   "jugador":"Messi Edición Naranja",    "pais":"Argentina 🇦🇷",    "tipo":"Edición Naranja"},
            {"id":"OC-CR7",     "jugador":"Ronaldo Edición Naranja",  "pais":"Portugal 🇵🇹",     "tipo":"Edición Naranja"},
            {"id":"OC-YML",     "jugador":"Yamal Edición Naranja",    "pais":"España 🇪🇸",       "tipo":"Edición Naranja"},
            {"id":"OC-MBP",     "jugador":"Mbappé Edición Naranja",   "pais":"Francia 🇫🇷",      "tipo":"Edición Naranja"},
            {"id":"OC-BEL",     "jugador":"Bellingham Edición Naranja","pais":"Inglaterra 🏴󠁧󠁢󠁥󠁮󠁧󠁿", "tipo":"Edición Naranja"},
            {"id":"OC-VIN",     "jugador":"Vinicius Edición Naranja", "pais":"Brasil 🇧🇷",       "tipo":"Edición Naranja"},
        ]
    },
}

COLORES_ESPECIALES = {
    "amber":  {"bg": ft.Colors.AMBER_50,   "border": ft.Colors.AMBER_300,  "header": ft.Colors.AMBER_600,  "badge": ft.Colors.AMBER_700},
    "purple": {"bg": ft.Colors.PURPLE_50,  "border": ft.Colors.PURPLE_200, "header": ft.Colors.PURPLE_600, "badge": ft.Colors.PURPLE_700},
    "blue":   {"bg": ft.Colors.BLUE_50,    "border": ft.Colors.BLUE_200,   "header": ft.Colors.BLUE_600,   "badge": ft.Colors.BLUE_700},
    "red":    {"bg": ft.Colors.RED_50,     "border": ft.Colors.RED_200,    "header": ft.Colors.RED_600,    "badge": ft.Colors.RED_700},
    "green":  {"bg": ft.Colors.GREEN_50,   "border": ft.Colors.GREEN_200,  "header": ft.Colors.GREEN_600,  "badge": ft.Colors.GREEN_700},
}

ARCHIVO_GUARDADO = "album_guardado.json"
SERVIDOR         = "https://stickers-app-production-555a.up.railway.app"

# Generar ID único por instalación
ID_FILE = "mi_id.txt"
if os.path.exists(ID_FILE):
    with open(ID_FILE) as f: MI_ID = f.read().strip()
else:
    MI_ID = str(uuid.uuid4())[:8]
    with open(ID_FILE, "w") as f: f.write(MI_ID)

USUARIOS_DB = [
    {"nombre": "Pedro","repetidas":["MEX10","MEX18","ARG5","BRA12","CAN3","GER14","FRA7"],
     "faltantes":["MEX5","ARG10","BRA20","USA1","URU11","ESP9","ITA4"],"lat":31.7333,"lon":-106.4833,"is_business":False},
    {"nombre": "Starbucks Misiones","repetidas":["MEX5","ARG10","BRA20","USA1","URU11","ESP9","ITA4"],
     "faltantes":["MEX10","MEX18","ARG5","CAN3","GER14","FRA7"],"lat":31.7400,"lon":-106.4900,"is_business":True},
]

PAISES = [
    ("GER","Alemania","DE"),("ANG","Angola","AO"),("KSA","Arabia Saudita","SA"),
    ("ARG","Argentina","AR"),("AUS","Australia","AU"),("AUT","Austria","AT"),
    ("BEL","Bélgica","BE"),("BRA","Brasil","BR"),("CMR","Camerún","CM"),
    ("CAN","Canadá","CA"),("CHI","Chile","CL"),("COL","Colombia","CO"),
    ("KOR","Corea del Sur","KR"),("CRC","Costa Rica","CR"),("CRO","Croacia","HR"),
    ("DEN","Dinamarca","DK"),("ECU","Ecuador","EC"),("EGY","Egipto","EG"),
    ("SCO","Escocia","GB"),("ESP","España","ES"),("USA","Estados Unidos","US"),
    ("FRA","Francia","FR"),("WAL","Gales","GB"),("GHA","Ghana","GH"),
    ("NED","Países Bajos","NL"),("ENG","Inglaterra","GB"),("IRN","Irán","IR"),
    ("IRQ","Irak","IQ"),("ITA","Italia","IT"),("JAM","Jamaica","JM"),
    ("JPN","Japón","JP"),("MAR","Marruecos","MA"),("MEX","México","MX"),
    ("NGA","Nigeria","NG"),("NZL","Nueva Zelanda","NZ"),("PAN","Panamá","PA"),
    ("PER","Perú","PE"),("POR","Portugal","PT"),("COD","Rep. D. Congo","CD"),
    ("SEN","Senegal","SN"),("SRB","Serbia","RS"),("SWE","Suecia","SE"),
    ("SUI","Suiza","CH"),("TUN","Túnez","TN"),("UKR","Ucrania","UA"),
    ("URU","Uruguay","UY"),("UZB","Uzbekistán","UZ"),("VEN","Venezuela","VE"),
]
TOTAL_PAISES=len(PAISES); TOTAL_ESTAMPAS=TOTAL_PAISES*20
PAISES_DICT={c:(n,i) for c,n,i in PAISES}

FALTA="falta";TENGO="tengo";REPETIDA="repetida"
C_FALTA=ft.Colors.BLUE_GREY_50;C_TENGO=ft.Colors.GREEN_500;C_REPETIDA=ft.Colors.BLUE_400
T_OSCURO=ft.Colors.BLUE_GREY_600;T_CLARO=ft.Colors.WHITE
COLORES_CONFETI=[ft.Colors.RED_400,ft.Colors.YELLOW_400,ft.Colors.GREEN_400,
                 ft.Colors.BLUE_400,ft.Colors.PURPLE_400,ft.Colors.ORANGE_400]

def estilo(e):
    if e==TENGO:    return "#10B981", T_CLARO
    if e==REPETIDA: return "#2563EB", T_CLARO
    return "#EEF2FF", "#1A3A6B"

def cargar():
    if os.path.exists(ARCHIVO_GUARDADO):
        try:
            with open(ARCHIVO_GUARDADO,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {}

def guardar(album):
    try:
        with open(ARCHIVO_GUARDADO,"w",encoding="utf-8") as f:
            json.dump(album,f,ensure_ascii=False,indent=2)
        return True
    except: return False

def stats(album):
    pc=tt=tr=0; det=[]
    for c,n,i in PAISES:
        t=sum(1 for x in range(1,21) if album.get(f"{c}{x}") in(TENGO,REPETIDA))
        r=sum(1 for x in range(1,21) if album.get(f"{c}{x}")==REPETIDA)
        comp=(t==20)
        if comp: pc+=1
        tt+=t; tr+=r; det.append((c,n,i,t,r,comp))
    return pc,tt,tr,round(tt/TOTAL_ESTAMPAS*100,1),det

def generar_qr_archivo(album, nombre, modo="intercambio"):
    reps=[k for k,v in album.items() if v==REPETIDA]
    fals=[f"{c}{i}" for c,_,_ in PAISES for i in range(1,21)
          if album.get(f"{c}{i}") not in(TENGO,REPETIDA)]
    if modo=="intercambio":
        # Formato completo para intercambio presencial
        texto=f"STICKERS|{MI_ID}|{nombre}|{','.join(reps)}|{','.join(fals[:50])}"
    else:
        texto=f"{nombre}|{','.join(reps)}"
    archivo=os.path.abspath(f"qr_{nombre.replace(' ','_')}.png")
    qr=qrcode.QRCode(version=None,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=6,border=3)
    qr.add_data(texto); qr.make(fit=True)
    qr.make_image(fill_color="black",back_color="white").save(archivo)
    return archivo, texto

def intercambio_qr(mi_album, sus_reps):
    sus_rep=set(sus_reps); mis_rep={k for k,v in mi_album.items() if v==REPETIDA}
    mis_fal={f"{c}{i}" for c,_,_ in PAISES for i in range(1,21)
             if mi_album.get(f"{c}{i}") not in(TENGO,REPETIDA)}
    return sorted(sus_rep&mis_fal), sorted(mis_rep)

def aplicar_intercambio(mi_album, me_da_list, le_doy_list):
    """Actualiza el álbum después de confirmar el intercambio presencial."""
    cambios = {"agregadas":[], "eliminadas":[]}
    # Las que recibo: las marco como TENGO
    for sticker in me_da_list:
        if mi_album.get(sticker) not in (TENGO, REPETIDA):
            mi_album[sticker] = TENGO
            cambios["agregadas"].append(sticker)
    # Las que doy: las quito (FALTA) si las tenía como REPETIDA
    for sticker in le_doy_list:
        if mi_album.get(sticker) == REPETIDA:
            mi_album[sticker] = FALTA
            cambios["eliminadas"].append(sticker)
    return cambios

# ── API SERVIDOR ─────────────────────────────────────────────────────
def servidor_activo():
    try: return requests.get(f"{SERVIDOR}/ping", timeout=2).ok
    except: return False

def registrar_usuario(album, nombre, lat, lon):
    reps=[k for k,v in album.items() if v==REPETIDA]
    fals=[f"{c}{i}" for c,_,_ in PAISES for i in range(1,21)
          if album.get(f"{c}{i}") not in(TENGO,REPETIDA)]
    try:
        r=requests.post(f"{SERVIDOR}/registrar",json={
            "usuario_id":MI_ID,"nombre":nombre,
            "repetidas":reps,"faltantes":fals,"lat":lat,"lon":lon
        },timeout=5)
        return r.json()
    except Exception as e: return {"ok":False,"mensaje":str(e)}

def buscar_grupos_api(lat, lon, radio_km=5.0):
    try:
        r=requests.post(f"{SERVIDOR}/buscar_grupos",json={
            "usuario_id":MI_ID,"lat":lat,"lon":lon,"radio_km":radio_km,"max_grupo":5
        },timeout=10)
        return r.json()
    except Exception as e: return {"ok":False,"grupos":[],"mensaje":str(e)}


def main(page: ft.Page):
    import base64, time as _time

    # ── SPLASH SCREEN ───────────────────────────────────────────────
    logo_widget = ft.Column([
        ft.Text("⚽", size=100, text_align=ft.TextAlign.CENTER),
        ft.Text("STICKERS", size=42, weight=ft.FontWeight.BOLD,
            color="#FCD34D", text_align=ft.TextAlign.CENTER),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)

    splash = ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1,-1), end=ft.Alignment(1,1),
            colors=["#0D1B3E","#1A3A6B","#2563EB"],
        ),
        content=ft.Column([
            ft.Container(expand=True),
            logo_widget,
            ft.Text("INTERCAMBIO DE ESTAMPAS", size=14, weight=ft.FontWeight.BOLD,
                color=ft.Colors.with_opacity(0.8,"#FCD34D"), text_align=ft.TextAlign.CENTER),
            ft.Container(height=20),
            ft.ProgressRing(color="#FCD34D", stroke_width=3, width=32, height=32),
            ft.Container(height=10),
            ft.Text("Cargando...", size=12, color=ft.Colors.with_opacity(0.6,"#FFFFFF")),
            ft.Container(expand=True),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
    )

    page.padding = 0
    page.add(splash)
    page.update()

    # Esperar 2.5 segundos
    import threading as _th2
    def _quitar_splash():
        _time.sleep(2.5)
        page.controls.clear()
        page.padding = 0
        _init_app(page)
        page.update()
    _th2.Thread(target=_quitar_splash, daemon=True).start()
    return

def _init_app(page: ft.Page):
    page.title="Stickers — Intercambio de Estampas"
    page.scroll="adaptive"; page.theme_mode=ft.ThemeMode.LIGHT
    page.bgcolor="#F0F4FF"; page.padding=0

    album=cargar(); pais_sel=["MEX"]; vista=["album"]
    nombre_u=["Mi Usuario"]; mi_lat,mi_lon=31.7350,-106.4850

    # ── GEOLOCALIZACIÓN AUTOMÁTICA ──────────────────────────────────
    def obtener_geolocalizacion():
        """Obtiene ubicación real del usuario via IP como fallback."""
        import threading as _th_geo
        def _geo():
            nonlocal mi_lat, mi_lon
            try:
                import requests as _req
                r = _req.get("https://ipapi.co/json/", timeout=5)
                data = r.json()
                if data.get("latitude") and data.get("longitude"):
                    mi_lat = float(data["latitude"])
                    mi_lon = float(data["longitude"])
            except: pass
        _th_geo.Thread(target=_geo, daemon=True).start()

    obtener_geolocalizacion()

    txt_t=ft.Text("0",size=20,weight=ft.FontWeight.BOLD,color="#10B981")
    txt_f=ft.Text("20",size=20,weight=ft.FontWeight.BOLD,color=ft.Colors.ORANGE_600)
    txt_r=ft.Text("0",size=20,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_400)
    barra=ft.ProgressBar(value=0,bgcolor=ft.Colors.with_opacity(0.15,"#2563EB"),color="#F59E0B",height=10,border_radius=5)
    txt_prog=ft.Text("0/20",size=11,weight=ft.FontWeight.BOLD,color=ft.Colors.GREY_600)
    txt_ph=ft.Text("México",size=12,weight=ft.FontWeight.BOLD,color="#FCD34D")
    txt_ih=ft.Text("[MX]",size=10,color=ft.Colors.with_opacity(0.7,"#FFFFFF"))

    snack=ft.SnackBar(content=ft.Text(""),bgcolor="#0D1B3E",
        behavior=ft.SnackBarBehavior.FLOATING)
    page.overlay.append(snack)
    grid_c=ft.Container(); vista_c=ft.Container()
    resultados=ft.ListView(spacing=12,padding=10,height=300)

    def snk(msg,color=ft.Colors.GREEN_700):
        snack.content=ft.Text(msg,color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD)
        snack.bgcolor=color; snack.open=True
        try: snack.update()
        except: pass

    def upd_cnt(prefix):
        t=sum(1 for k,v in album.items() if k.startswith(prefix) and v in(TENGO,REPETIDA))
        r=sum(1 for k,v in album.items() if k.startswith(prefix) and v==REPETIDA)
        txt_t.value=str(t-r);txt_f.value=str(max(20-t,0));txt_r.value=str(r)
        barra.value=t/20;txt_prog.value=f"{t}/20"
        try: txt_t.update();txt_f.update();txt_r.update();barra.update();txt_prog.update()
        except: pass

    def celebrar(np):
        piezas=[ft.Container(width=random.randint(8,16),height=random.randint(8,16),
            bgcolor=random.choice(COLORES_CONFETI),border_radius=random.randint(0,8),
            left=random.randint(10,380),top=random.randint(10,200),
            rotate=ft.Rotate(random.uniform(0,3.14)),opacity=random.uniform(0.7,1.0)) for _ in range(30)]
        dlg=ft.AlertDialog(modal=True,bgcolor=ft.Colors.WHITE,shape=ft.RoundedRectangleBorder(radius=24),
            content=ft.Container(width=400,content=ft.Column([
                ft.Stack([ft.Stack(piezas,width=400,height=220),
                    ft.Container(width=400,height=220,alignment=ft.Alignment(0,0),
                        content=ft.Column([ft.Text("🏆",size=60),
                            ft.Text("¡País Completado!",size=22,weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_GREY_900,text_align=ft.TextAlign.CENTER)],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=4))]),
                ft.Container(padding=ft.Padding(20,0,20,20),content=ft.Column([
                    ft.Text("¡Completaste las 20 estampas de",size=14,color=ft.Colors.GREY_600,text_align=ft.TextAlign.CENTER),
                    ft.Text(np,size=20,weight=ft.FontWeight.BOLD,color=ft.Colors.GREEN_700,text_align=ft.TextAlign.CENTER),
                ],horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=6))],spacing=0)),
            actions=[ft.Button(content=ft.Row([ft.Icon(ft.Icons.CELEBRATION,color=ft.Colors.WHITE),
                ft.Text("¡Genial!",color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD)],tight=True,spacing=6),
                on_click=lambda e:cerrar(dlg),
                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600,color=ft.Colors.WHITE,
                    padding=ft.Padding(24,12,24,12),shape=ft.RoundedRectangleBorder(radius=12)))],
            actions_alignment=ft.MainAxisAlignment.CENTER)
        page.overlay.append(dlg);dlg.open=True;page.update()

    def cerrar(dlg): dlg.open=False;page.update()

    def construir_grid(prefix):
        celdas={};ctrl=[];celebrado=[False]
        def check():
            if celebrado[0]: return
            if sum(1 for i in range(1,21) if album.get(f"{prefix}{i}") in(TENGO,REPETIDA))==20:
                celebrado[0]=True;n,_=PAISES_DICT.get(prefix,(prefix,""));celebrar(n)
        def tap(e,num):
            k=f"{prefix}{num}";nuevo=TENGO if album.get(k,FALTA)==FALTA else FALTA
            album[k]=nuevo;guardar(album)
            bg,fg=estilo(nuevo);c=celdas[num];c.bgcolor=bg;c.content.color=fg
            c.border=None if nuevo!=FALTA else ft.Border.all(1,ft.Colors.BLUE_GREY_200)
            c.shadow=ft.BoxShadow(blur_radius=6,color=ft.Colors.BLACK26,offset=ft.Offset(0,2)) if nuevo!=FALTA else None
            c.update();upd_cnt(prefix);check()
        def dtap(e,num):
            k=f"{prefix}{num}";album[k]=REPETIDA;guardar(album)
            bg,fg=estilo(REPETIDA);c=celdas[num];c.bgcolor=bg;c.content.color=fg
            c.border=None;c.shadow=ft.BoxShadow(blur_radius=6,color=ft.Colors.BLACK26,offset=ft.Offset(0,2))
            c.update();upd_cnt(prefix);check()
        # Tamaño adaptado a móvil: 4 columnas × 5 filas, celdas más compactas
        CELL_W=56; CELL_H=52; CELL_R=10; FONT_SZ=14; CELL_SPACING=6; ROW_COLS=5
        for i in range(1,21):
            ea=album.get(f"{prefix}{i}",FALTA);bg,fg=estilo(ea)
            cont=ft.Container(
                content=ft.Text(str(i),color=fg,weight=ft.FontWeight.BOLD,size=FONT_SZ),
                bgcolor=bg,border_radius=CELL_R,width=CELL_W,height=CELL_H,alignment=ft.Alignment(0,0),
                border=ft.Border.all(1.5, ft.Colors.with_opacity(0.2,"#2563EB")) if ea==FALTA
                       else (ft.Border.all(2, "#F59E0B") if ea==REPETIDA else ft.Border.all(2, "#10B981")),
                shadow=ft.BoxShadow(blur_radius=8,
                    color=ft.Colors.with_opacity(0.4, "#F59E0B" if ea==REPETIDA else "#10B981"),
                    offset=ft.Offset(0,3)) if ea!=FALTA else None)
            celdas[i]=cont
            ctrl.append(ft.GestureDetector(content=cont,on_tap=lambda e,n=i:tap(e,n),on_double_tap=lambda e,n=i:dtap(e,n)))
        filas=[]
        for f in range(0,20,ROW_COLS): filas.append(ft.Row(ctrl[f:f+ROW_COLS],spacing=CELL_SPACING,alignment=ft.MainAxisAlignment.CENTER))
        return ft.Column(filas,spacing=CELL_SPACING)

    def upd_tablero(prefix):
        n,iso=PAISES_DICT.get(prefix,(prefix,"??"))
        txt_ph.value=n;txt_ih.value=f"[{iso}]"
        try: txt_ph.update();txt_ih.update()
        except: pass
        grid_c.content=construir_grid(prefix)
        try: grid_c.update()
        except: pass
        upd_cnt(prefix)

    # ── VISTA GRUPOS ─────────────────────────────────────────────────
    def vista_grupos():
        txt_estado=ft.Text("",size=13,color=ft.Colors.GREY_600,text_align=ft.TextAlign.CENTER)
        txt_servidor=ft.Text("",size=12)
        lista_grupos=ft.Column([],spacing=12,scroll=ft.ScrollMode.AUTO)
        campo_nombre=ft.TextField(label="Tu nombre",value=nombre_u[0],width=220,border_radius=10,bgcolor=ft.Colors.WHITE)
        campo_radio=ft.TextField(label="Radio (km)",value="5",width=100,border_radius=10,bgcolor=ft.Colors.WHITE)
        buscando=[False]

        # Verificar servidor
        def check_server():
            if servidor_activo():
                txt_servidor.value="🟢 Servidor conectado"
                txt_servidor.color=ft.Colors.GREEN_700
            else:
                txt_servidor.value="🔴 Servidor desconectado — corre servidor.py primero"
                txt_servidor.color=ft.Colors.RED_700
            try: txt_servidor.update()
            except: pass

        def registrar_y_buscar(e):
            if buscando[0]: return
            buscando[0]=True
            nombre_u[0]=campo_nombre.value or "Mi Usuario"
            try: radio=float(campo_radio.value)
            except: radio=5.0

            txt_estado.value="📡 Registrando tu álbum en el servidor..."
            txt_estado.color=ft.Colors.BLUE_600
            lista_grupos.controls.clear()
            try: txt_estado.update();lista_grupos.update()
            except: pass

            def _buscar():
                try:
                    # Registrar
                    res_reg=registrar_usuario(album,nombre_u[0],mi_lat,mi_lon)
                    if not res_reg.get("ok"):
                        txt_estado.value=f"❌ {res_reg.get('mensaje','Error al registrar')}"
                        txt_estado.color=ft.Colors.RED_700
                        try: txt_estado.update()
                        except: pass
                        buscando[0]=False
                        return

                    txt_estado.value="🔍 Buscando grupos de intercambio..."
                    txt_estado.color=ft.Colors.BLUE_600
                    try: txt_estado.update()
                    except: pass

                    # Buscar grupos
                    res=buscar_grupos_api(mi_lat,mi_lon,radio)
                    grupos=res.get("grupos",[])

                    lista_grupos.controls.clear()

                    if not grupos:
                        lista_grupos.controls.append(
                            ft.Container(alignment=ft.Alignment(0,0),padding=30,
                                content=ft.Column([
                                    ft.Text("😔",size=40),
                                    ft.Text("No se encontraron grupos de intercambio cercanos",
                                        color=ft.Colors.GREY_500,italic=True,
                                        text_align=ft.TextAlign.CENTER,size=14),
                                    ft.Text("Pide a tus amigos que instalen la app y se registren",
                                        color=ft.Colors.GREY_400,size=12,
                                        text_align=ft.TextAlign.CENTER),
                                ],horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=8))
                        )
                        txt_estado.value=f"✅ Búsqueda completa — {res.get('mensaje','')}"
                    else:
                        txt_estado.value=f"✅ ¡Se encontraron {len(grupos)} grupos posibles!"
                        txt_estado.color=ft.Colors.GREEN_700
                        for i,g in enumerate(grupos):
                            lista_grupos.controls.append(tarjeta_grupo(g,i+1))

                    try: txt_estado.update();lista_grupos.update();page.update()
                    except: pass

                except Exception as ex:
                    txt_estado.value=f"❌ Error: {ex}"
                    txt_estado.color=ft.Colors.RED_700
                    try: txt_estado.update()
                    except: pass
                finally:
                    buscando[0]=False

            threading.Thread(target=_buscar,daemon=True).start()

        def tarjeta_grupo(g, num):
            miembros=g["miembros"]; tam=g["tamaño"]; total=g["total_estampas"]

            # Color por tamaño del grupo
            if tam>=4: color_header=ft.Colors.PURPLE_600; emoji="🎯"
            elif tam==3: color_header=ft.Colors.BLUE_600; emoji="🔄"
            else: color_header=ft.Colors.GREEN_600; emoji="🤝"

            filas_miembros=[]
            for m in miembros:
                es_yo=(m["id"]==MI_ID)
                recibe_de=m.get("recibe",[])
                estampas_recibe=[]
                for r in recibe_de:
                    for est in r["estampas"]:
                        estampas_recibe.append(f"{est} (de {r['de']})")

                filas_miembros.append(
                    ft.Container(
                        padding=ft.Padding(10,8,10,8),
                        border_radius=8,
                        bgcolor=ft.Colors.BLUE_50 if es_yo else ft.Colors.GREY_50,
                        border=ft.Border.all(1,ft.Colors.BLUE_200 if es_yo else ft.Colors.GREY_200),
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PERSON,
                                    color=ft.Colors.BLUE_600 if es_yo else ft.Colors.GREY_600,size=16),
                                ft.Text(m["nombre"]+(" (Tú)" if es_yo else ""),
                                    size=13,weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_800 if es_yo else ft.Colors.BLUE_GREY_800),
                                ft.Container(expand=True),
                                ft.Text(f"📍 {m['dist_km']} km",size=11,color=ft.Colors.GREY_500),
                            ],spacing=6),
                            ft.Text(
                                f"Recibe: {', '.join(estampas_recibe)}" if estampas_recibe else "No recibe en este grupo",
                                size=12,
                                color=ft.Colors.GREEN_700 if estampas_recibe else ft.Colors.GREY_400,
                            ),
                        ],spacing=4)
                    )
                )

            return ft.Card(
                elevation=4,
                content=ft.Container(
                    padding=16,border_radius=16,bgcolor=ft.Colors.WHITE,
                    border=ft.Border.all(1.5,color_header),
                    content=ft.Column([
                        # Header
                        ft.Container(
                            padding=ft.Padding(12,10,12,10),
                            border_radius=10,
                            bgcolor=color_header,
                            content=ft.Row([
                                ft.Text(emoji,size=20),
                                ft.Column([
                                    ft.Text(f"Grupo #{num} — {tam} personas",
                                        size=15,weight=ft.FontWeight.BOLD,color=ft.Colors.WHITE),
                                    ft.Text(f"{total} estampas intercambiables en total",
                                        size=12,color=ft.Colors.WHITE70),
                                ],spacing=2,expand=True),
                                ft.Container(
                                    padding=ft.Padding(8,4,8,4),
                                    border_radius=20,
                                    bgcolor=ft.Colors.WHITE24,
                                    content=ft.Text(f"{tam} 👥",size=14,color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD),
                                ),
                            ],spacing=10),
                        ),
                        ft.Divider(height=10,color=ft.Colors.GREY_100),
                        # Miembros
                        ft.Text("Participantes:",size=13,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_GREY_700),
                        ft.Column(filas_miembros,spacing=6),
                        ft.Divider(height=8,color=ft.Colors.GREY_100),
                        # Botón coordinar
                        ft.Button(
                            content=ft.Row([
                                ft.Icon(ft.Icons.GROUP,color=ft.Colors.WHITE,size=16),
                                ft.Text("¡Coordinar encuentro!",color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD,size=13),
                            ],tight=True,spacing=6),
                            on_click=lambda e,g=g: mostrar_coordinacion(g),
                            style=ft.ButtonStyle(
                                bgcolor=color_header,color=ft.Colors.WHITE,
                                padding=ft.Padding(16,10,16,10),
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                        ),
                    ],spacing=10)
                )
            )

        def mostrar_coordinacion(g):
            miembros=g["miembros"]
            nombres=", ".join(m["nombre"] for m in miembros)
            dlg=ft.AlertDialog(
                modal=True,bgcolor=ft.Colors.WHITE,shape=ft.RoundedRectangleBorder(radius=20),
                title=ft.Text("📅 Coordinar Encuentro",weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_GREY_900),
                content=ft.Container(width=380,content=ft.Column([
                    ft.Container(padding=12,border_radius=10,bgcolor=ft.Colors.BLUE_50,
                        content=ft.Column([
                            ft.Text("👥 Participantes:",size=13,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_800),
                            ft.Text(nombres,size=13,color=ft.Colors.BLUE_900),
                        ],spacing=4)),
                    ft.Container(padding=12,border_radius=10,bgcolor=ft.Colors.GREEN_50,
                        content=ft.Column([
                            ft.Text("📍 Punto de encuentro sugerido:",size=13,weight=ft.FontWeight.BOLD,color=ft.Colors.GREEN_800),
                            ft.Text("Centro del grupo — cerca de todos",size=13,color=ft.Colors.GREEN_900),
                        ],spacing=4)),
                    ft.Container(padding=12,border_radius=10,bgcolor=ft.Colors.AMBER_50,
                        content=ft.Column([
                            ft.Text("💡 Cómo coordinar:",size=13,weight=ft.FontWeight.BOLD,color=ft.Colors.AMBER_800),
                            ft.Text("1. Comparte tu QR con el grupo\n2. Acuerden lugar y hora por WhatsApp\n3. ¡Intercambien sus estampas!",
                                size=12,color=ft.Colors.AMBER_900),
                        ],spacing=4)),
                ],spacing=10)),
                actions=[
                    ft.Button(content=ft.Text("Cerrar",color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD),
                        on_click=lambda e:cerrar(dlg),
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600,color=ft.Colors.WHITE,
                            padding=ft.Padding(20,10,20,10),shape=ft.RoundedRectangleBorder(radius=10))),
                ],
                actions_alignment=ft.MainAxisAlignment.CENTER,
            )
            page.overlay.append(dlg);dlg.open=True;page.update()

        # Check servidor al abrir
        threading.Thread(target=check_server,daemon=True).start()

        btn_buscar=ft.Button(
            content=ft.Row([ft.Icon(ft.Icons.GROUP_WORK,color=ft.Colors.WHITE),
                ft.Text("Buscar Grupos de Intercambio",color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD,size=15)],
                tight=True,spacing=8),
            on_click=registrar_y_buscar,
            style=ft.ButtonStyle(bgcolor="#2563EB",color=ft.Colors.WHITE,
                padding=ft.Padding(24,14,24,14),shape=ft.RoundedRectangleBorder(radius=12),elevation=4),
        )

        return ft.Container(padding=ft.Padding(20,16,20,24),content=ft.Column([
            ft.Container(padding=20,bgcolor=ft.Colors.WHITE,border_radius=18,
                shadow=ft.BoxShadow(blur_radius=12,color=ft.Colors.BLACK12,offset=ft.Offset(0,3)),
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.GROUP_WORK,color=ft.Colors.PURPLE_600,size=22),
                        ft.Text("Intercambio Grupal",size=17,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_GREY_800)],spacing=8),
                    txt_servidor,
                    ft.Text("La app busca grupos de 2-5 personas cercanas que puedan intercambiar estampas entre sí de forma circular.",
                        size=12,color=ft.Colors.GREY_500),
                    ft.Divider(height=8,color=ft.Colors.GREY_100),
                    ft.Row([campo_nombre,campo_radio],spacing=10),
                    ft.Row([btn_buscar],alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([txt_estado],alignment=ft.MainAxisAlignment.CENTER),
                ],spacing=12)),
            ft.Divider(height=10,color=ft.Colors.TRANSPARENT),
            lista_grupos,
        ],spacing=10,scroll=ft.ScrollMode.AUTO))

    # ── VISTA QR ────────────────────────────────────────────────────
    def vista_qr():
        import io, base64
        txt_st=ft.Text("",size=13,color=ft.Colors.GREY_600,text_align=ft.TextAlign.CENTER)
        res_scan=ft.Column([],spacing=8)
        campo=ft.TextField(label="Tu nombre",value=nombre_u[0],width=260,border_radius=10,bgcolor=ft.Colors.WHITE)
        qr_img=ft.Image(src="/tmp/qr_temp.png",visible=False,width=220,height=220,fit="contain")
        txt_qr_data=ft.Text("",size=0,visible=False)  # guarda datos del QR para pegar/compartir

        def gen(e):
            nombre_u[0]=campo.value or "Mi Usuario"
            try:
                reps=[k for k,v in album.items() if v==REPETIDA]
                fals=[f"{c}{i}" for c,_,_ in PAISES for i in range(1,21)
                      if album.get(f"{c}{i}") not in(TENGO,REPETIDA)]
                texto_qr=f"STICKERS|{MI_ID}|{nombre_u[0]}|{','.join(reps)}|{','.join(fals[:50])}"
                # Generar QR en memoria (sin guardar archivo)
                qr=qrcode.QRCode(version=None,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=8,border=3)
                qr.add_data(texto_qr); qr.make(fit=True)
                img=qr.make_image(fill_color="black",back_color="white")
                buf=io.BytesIO(); img.save(buf,format="PNG")
                b64=base64.b64encode(buf.getvalue()).decode()
                import os as _os2
                _qr_path = _os2.path.join(_os2.path.dirname(_os2.path.abspath(__file__)), "qr_temp.png")
                with open(_qr_path, "wb") as _qf:
                    _qf.write(buf.getvalue())
                qr_img.src=_qr_path; qr_img.visible=True
                txt_qr_data.value=texto_qr
                txt_st.value=f"✅ QR listo — muéstraselo a la otra persona"
                txt_st.color=ft.Colors.GREEN_700
            except Exception as ex:
                txt_st.value=f"❌ Error: {ex}"; txt_st.color=ft.Colors.RED_700
            try: txt_st.update();qr_img.update();page.update()
            except: pass

        def procesar_qr_texto(leido):
            """Procesa el texto del QR y muestra resultado de intercambio."""
            if leido.startswith("STICKERS|"):
                partes=leido.split("|")
                nom=partes[2] if len(partes)>2 else "Otro"
                reps=partes[3].split(",") if len(partes)>3 and partes[3] else []
            else:
                partes=leido.split("|",1)
                nom=partes[0]
                reps=partes[1].split(",") if len(partes)>1 and partes[1] else []

            me_da,le_doy=intercambio_qr(album,reps)
            txt_st.value=f"✅ QR de {nom} leído"; txt_st.color=ft.Colors.GREEN_700

            res_scan.controls.clear()
            res_scan.controls.append(
                ft.Container(padding=16,border_radius=14,bgcolor=ft.Colors.WHITE,
                    border=ft.Border.all(1.5,ft.Colors.BLUE_200),
                    shadow=ft.BoxShadow(blur_radius=8,color=ft.Colors.BLACK12,offset=ft.Offset(0,2)),
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.SWAP_HORIZ,color=ft.Colors.BLUE_600,size=22),
                            ft.Text(f"Intercambio con {nom}",size=16,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_GREY_900)],spacing=8),
                        ft.Divider(height=8,color=ft.Colors.GREY_100),
                        ft.Container(bgcolor=ft.Colors.GREEN_50,border_radius=10,padding=12,
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.Icons.ARROW_DOWNWARD,color=ft.Colors.GREEN_700,size=16),
                                    ft.Text(f"Recibes ({len(me_da)} estampas)",size=13,weight=ft.FontWeight.BOLD,color=ft.Colors.GREEN_700)]),
                                ft.Text(", ".join(me_da) if me_da else "Ninguna",size=13,color=ft.Colors.GREEN_900),
                            ],spacing=4)),
                        ft.Container(bgcolor=ft.Colors.BLUE_50,border_radius=10,padding=12,
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.Icons.ARROW_UPWARD,color=ft.Colors.BLUE_700,size=16),
                                    ft.Text(f"Das ({len(le_doy)} estampas)",size=13,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_700)]),
                                ft.Text(", ".join(le_doy) if le_doy else "Ninguna",size=13,color=ft.Colors.BLUE_900),
                            ],spacing=4)),
                        ft.Divider(height=8,color=ft.Colors.GREY_100),
                        ft.Button(
                            content=ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE,color=ft.Colors.WHITE,size=18),
                                ft.Text("✅ Confirmar Intercambio",color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD,size=14),
                            ],tight=True,spacing=8),
                            on_click=lambda e,md=me_da,ld=le_doy,n=nom: confirmar_intercambio(md,ld,n),
                            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600,color=ft.Colors.WHITE,
                                padding=ft.Padding(16,12,16,12),shape=ft.RoundedRectangleBorder(radius=12),elevation=4),
                        ),
                    ],spacing=10))
            )
            try: txt_st.update();res_scan.update();page.update()
            except: pass

        def pegar_qr(e):
            """El usuario pega manualmente el texto QR de la otra persona."""
            campo_pegar=ft.TextField(
                label="Pega aquí el texto QR de la otra persona",
                multiline=True,min_lines=3,max_lines=5,
                border_radius=10,bgcolor=ft.Colors.WHITE,width=320)
            def leer(ev):
                txt=campo_pegar.value.strip()
                if txt:
                    dlg.open=False; page.update()
                    procesar_qr_texto(txt)
                else:
                    campo_pegar.error_text="Pega el texto del QR primero"
                    try: campo_pegar.update()
                    except: pass
            dlg=ft.AlertDialog(
                modal=True,bgcolor=ft.Colors.WHITE,shape=ft.RoundedRectangleBorder(radius=16),
                title=ft.Text("Pegar código QR",weight=ft.FontWeight.BOLD,size=16),
                content=ft.Container(width=340,content=ft.Column([
                    ft.Text("Pide a la otra persona que copie su código QR y te lo mande por WhatsApp.",
                        size=13,color=ft.Colors.GREY_600),
                    campo_pegar,
                ],spacing=10)),
                actions=[
                    ft.Button(content=ft.Text("Cancelar",color=ft.Colors.GREY_700),
                        on_click=lambda e: cerrar(dlg),
                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_200,padding=ft.Padding(16,10,16,10),
                            shape=ft.RoundedRectangleBorder(radius=10))),
                    ft.Button(content=ft.Text("Leer QR",color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD),
                        on_click=leer,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600,color=ft.Colors.WHITE,
                            padding=ft.Padding(16,10,16,10),shape=ft.RoundedRectangleBorder(radius=10))),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.overlay.append(dlg); dlg.open=True; page.update()

        def confirmar_intercambio(me_da, le_doy, nombre_otro):
            if not me_da and not le_doy:
                snk("⚠️ No hay estampas para intercambiar", ft.Colors.ORANGE_700)
                return
            # Mostrar diálogo de confirmación
            def ejecutar(e):
                dlg.open=False; page.update()
                cambios = aplicar_intercambio(album, me_da, le_doy)
                guardar(album)
                upd_tablero(pais_sel[0])
                # Mostrar resumen
                msg = f"🎉 ¡Intercambio completado con {nombre_otro}!\n"
                if cambios['agregadas']: msg += f"\n+{len(cambios['agregadas'])} estampas nuevas: {', '.join(cambios['agregadas'])}"
                if cambios['eliminadas']: msg += f"\n-{len(cambios['eliminadas'])} entregadas: {', '.join(cambios['eliminadas'])}"
                res_scan.controls.clear()
                res_scan.controls.append(
                    ft.Container(padding=20,border_radius=14,bgcolor=ft.Colors.GREEN_50,
                        border=ft.Border.all(2,ft.Colors.GREEN_400),
                        shadow=ft.BoxShadow(blur_radius=8,color=ft.Colors.BLACK12,offset=ft.Offset(0,2)),
                        content=ft.Column([
                            ft.Row([ft.Icon(ft.Icons.CELEBRATION,color=ft.Colors.GREEN_700,size=28),
                                ft.Text("¡Intercambio Completado!",size=18,weight=ft.FontWeight.BOLD,color=ft.Colors.GREEN_800)],spacing=8),
                            ft.Divider(height=6,color=ft.Colors.GREEN_200),
                            ft.Text(f"Con: {nombre_otro}",size=14,weight=ft.FontWeight.BOLD,color=ft.Colors.GREEN_700),
                            ft.Container(bgcolor=ft.Colors.WHITE,border_radius=10,padding=12,
                                content=ft.Column([
                                    ft.Text(f"✅ Recibiste: {', '.join(cambios['agregadas']) if cambios['agregadas'] else 'Ninguna'}",
                                        size=13,color=ft.Colors.GREEN_800),
                                    ft.Text(f"📤 Entregaste: {', '.join(cambios['eliminadas']) if cambios['eliminadas'] else 'Ninguna'}",
                                        size=13,color=ft.Colors.BLUE_800),
                                ],spacing=6)),
                            ft.Text("Tu álbum ha sido actualizado automáticamente 🎯",
                                size=12,color=ft.Colors.GREEN_600,italic=True,text_align=ft.TextAlign.CENTER),
                        ],spacing=8,horizontal_alignment=ft.CrossAxisAlignment.START))
                )
                try: res_scan.update(); page.update()
                except: pass

            dlg = ft.AlertDialog(
                modal=True,bgcolor=ft.Colors.WHITE,shape=ft.RoundedRectangleBorder(radius=20),
                title=ft.Row([ft.Icon(ft.Icons.SWAP_HORIZ,color=ft.Colors.BLUE_600,size=26),
                    ft.Text("Confirmar Intercambio",weight=ft.FontWeight.BOLD,size=18,color=ft.Colors.BLUE_GREY_900)],spacing=8),
                content=ft.Container(width=400,content=ft.Column([
                    ft.Text(f"¿Confirmas el intercambio con {nombre_otro}?",size=14,color=ft.Colors.BLUE_GREY_700),
                    ft.Divider(height=8,color=ft.Colors.GREY_100),
                    ft.Container(bgcolor=ft.Colors.GREEN_50,border_radius=10,padding=12,
                        content=ft.Column([
                            ft.Text(f"Recibirás ({len(me_da)}):",size=13,weight=ft.FontWeight.BOLD,color=ft.Colors.GREEN_700),
                            ft.Text(", ".join(me_da) if me_da else "Ninguna",size=13,color=ft.Colors.GREEN_900),
                        ],spacing=4)),
                    ft.Container(bgcolor=ft.Colors.BLUE_50,border_radius=10,padding=12,
                        content=ft.Column([
                            ft.Text(f"Entregarás ({len(le_doy)}):",size=13,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_700),
                            ft.Text(", ".join(le_doy) if le_doy else "Ninguna",size=13,color=ft.Colors.BLUE_900),
                        ],spacing=4)),
                    ft.Container(bgcolor=ft.Colors.AMBER_50,border_radius=10,padding=10,
                        border=ft.Border.all(1,ft.Colors.AMBER_200),
                        content=ft.Row([
                            ft.Icon(ft.Icons.INFO_OUTLINE,color=ft.Colors.AMBER_700,size=16),
                            ft.Text("Tu álbum se actualizará automáticamente",size=12,color=ft.Colors.AMBER_800),
                        ],spacing=6)),
                ],spacing=10)),
                actions=[
                    ft.Button(content=ft.Text("Cancelar",color=ft.Colors.GREY_700,weight=ft.FontWeight.BOLD),
                        on_click=lambda e: cerrar(dlg),
                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_200,color=ft.Colors.GREY_700,
                            padding=ft.Padding(20,10,20,10),shape=ft.RoundedRectangleBorder(radius=10))),
                    ft.Button(content=ft.Row([ft.Icon(ft.Icons.CHECK,color=ft.Colors.WHITE),
                        ft.Text("¡Confirmar!",color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD)],tight=True,spacing=6),
                        on_click=ejecutar,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600,color=ft.Colors.WHITE,
                            padding=ft.Padding(20,10,20,10),shape=ft.RoundedRectangleBorder(radius=10))),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.overlay.append(dlg); dlg.open=True; page.update()

        btn_gen=ft.Button(content=ft.Row([ft.Icon(ft.Icons.QR_CODE_2,color=ft.Colors.WHITE),
            ft.Text("Generar mi QR",color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD)],tight=True,spacing=8),
            on_click=gen,style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600,color=ft.Colors.WHITE,
                padding=ft.Padding(20,12,20,12),shape=ft.RoundedRectangleBorder(radius=12),elevation=4))
        btn_pegar=ft.Button(content=ft.Row([ft.Icon(ft.Icons.CONTENT_PASTE,color=ft.Colors.WHITE),
            ft.Text("Leer QR de otro",color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD)],tight=True,spacing=8),
            on_click=pegar_qr,style=ft.ButtonStyle(bgcolor=ft.Colors.PURPLE_600,color=ft.Colors.WHITE,
                padding=ft.Padding(20,12,20,12),shape=ft.RoundedRectangleBorder(radius=12),elevation=4))

        return ft.Container(padding=ft.Padding(20,16,20,24),content=ft.Column([
            ft.Container(padding=20,bgcolor=ft.Colors.WHITE,border_radius=18,
                shadow=ft.BoxShadow(blur_radius=12,color=ft.Colors.BLACK12,offset=ft.Offset(0,3)),
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.QR_CODE_2,color=ft.Colors.BLUE_600,size=22),
                        ft.Text("Mi Código QR",size=17,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_GREY_800)],spacing=8),
                    ft.Container(padding=10,border_radius=10,bgcolor=ft.Colors.BLUE_50,
                        border=ft.Border.all(1,ft.Colors.BLUE_100),
                        content=ft.Column([
                            ft.Text("📋 Cómo intercambiar:",size=12,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_800),
                            ft.Text("1️⃣  Genera tu QR y toma captura de pantalla",size=12,color=ft.Colors.BLUE_700),
                            ft.Text("2️⃣  Mándasela por WhatsApp a la otra persona",size=12,color=ft.Colors.BLUE_700),
                            ft.Text("3️⃣  Pídele que haga lo mismo y pega su código aquí",size=12,color=ft.Colors.BLUE_700),
                            ft.Text("4️⃣  Confirma el intercambio — el álbum se actualiza solo 🎯",size=12,color=ft.Colors.BLUE_700),
                        ],spacing=3)),
                    campo,
                    ft.Row([btn_gen],alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([qr_img],alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([txt_st],alignment=ft.MainAxisAlignment.CENTER),
                ],spacing=12)),
            ft.Divider(height=10,color=ft.Colors.TRANSPARENT),
            ft.Container(padding=20,bgcolor=ft.Colors.WHITE,border_radius=18,
                shadow=ft.BoxShadow(blur_radius=12,color=ft.Colors.BLACK12,offset=ft.Offset(0,3)),
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.CONTENT_PASTE,color=ft.Colors.PURPLE_600,size=22),
                        ft.Text("Leer QR de otro",size=17,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_GREY_800)],spacing=8),
                    ft.Text("La otra persona genera su QR, lo copia como texto y te lo manda por WhatsApp.",
                        size=12,color=ft.Colors.GREY_600),
                    ft.Row([btn_pegar],alignment=ft.MainAxisAlignment.CENTER),
                    res_scan,
                ],spacing=12)),
        ],spacing=10,scroll=ft.ScrollMode.AUTO))

    # ── VISTA STATS ─────────────────────────────────────────────────
    def vista_stats():
        pc,tt,tr,pct,det=stats(album)
        def tc(titulo,val,sub,color,icono):
            return ft.Container(expand=True,padding=16,border_radius=16,bgcolor=ft.Colors.WHITE,
                border=ft.Border.all(1,ft.Colors.GREY_200),
                shadow=ft.BoxShadow(blur_radius=8,color=ft.Colors.BLACK12,offset=ft.Offset(0,2)),
                content=ft.Column([ft.Icon(icono,color=color,size=26),
                    ft.Text(str(val),size=28,weight=ft.FontWeight.BOLD,color=color),
                    ft.Text(titulo,size=12,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_GREY_700),
                    ft.Text(sub,size=11,color=ft.Colors.GREY_500)],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=4))
        resumen=ft.Row([
            tc("Países\nCompletos",pc,f"de {TOTAL_PAISES}",ft.Colors.GREEN_600,ft.Icons.EMOJI_EVENTS),
            tc("Estampas\nColectadas",tt,f"de {TOTAL_ESTAMPAS}",ft.Colors.BLUE_600,ft.Icons.COLLECTIONS),
            tc("Álbum\nCompletado",f"{pct}%","del total",ft.Colors.PURPLE_600,ft.Icons.PIE_CHART),
            tc("Repetidas\nTotales",tr,"para intercambio",ft.Colors.ORANGE_600,ft.Icons.COPY_ALL),
        ],spacing=10)
        det_ord=sorted(det,key=lambda x:(not x[5],-x[3]))
        filas=[]
        for c,n,iso,t,r,comp in det_ord:
            cb=ft.Colors.GREEN_500 if comp else(ft.Colors.BLUE_400 if t>0 else ft.Colors.GREY_300)
            filas.append(ft.Container(padding=ft.Padding(12,8,12,8),border_radius=10,
                bgcolor=ft.Colors.GREEN_50 if comp else ft.Colors.WHITE,
                border=ft.Border.all(1,ft.Colors.GREEN_200 if comp else ft.Colors.GREY_100),
                content=ft.Row([
                    ft.Container(width=36,height=36,border_radius=18,
                        bgcolor=ft.Colors.GREEN_500 if comp else ft.Colors.GREY_200,
                        alignment=ft.Alignment(0,0),
                        content=ft.Text("✓" if comp else str(t),
                            color=ft.Colors.WHITE if comp else ft.Colors.GREY_600,size=13,weight=ft.FontWeight.BOLD)),
                    ft.Column([
                        ft.Row([ft.Text(f"[{iso}] {n}",size=13,weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREEN_800 if comp else ft.Colors.BLUE_GREY_800),
                            ft.Container(expand=True),ft.Text(f"{t}/20",size=12,color=ft.Colors.GREY_600)]),
                        ft.ProgressBar(value=t/20,bgcolor=ft.Colors.GREY_100,color=cb,height=6,border_radius=3),
                    ],expand=True,spacing=4),
                ],spacing=10,vertical_alignment=ft.CrossAxisAlignment.CENTER)))
        return ft.Container(padding=ft.Padding(20,16,20,24),content=ft.Column([
            resumen,ft.Divider(height=8,color=ft.Colors.TRANSPARENT),
            ft.Container(padding=20,bgcolor=ft.Colors.WHITE,border_radius=18,
                shadow=ft.BoxShadow(blur_radius=12,color=ft.Colors.BLACK12,offset=ft.Offset(0,3)),
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.BAR_CHART,color=ft.Colors.PURPLE_600,size=22),
                        ft.Text("Progreso General",size=17,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_GREY_800)],spacing=8),
                    ft.Column([ft.Row([ft.Text("Progreso general",size=13,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_GREY_700),
                        ft.Text(f"{pct}%",size=13,weight=ft.FontWeight.BOLD,color=ft.Colors.GREEN_600)],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.ProgressBar(value=pct/100,bgcolor=ft.Colors.GREY_200,color=ft.Colors.GREEN_500,height=16,border_radius=8)],spacing=6),
                ],spacing=12)),
            ft.Divider(height=6,color=ft.Colors.TRANSPARENT),
            ft.Container(padding=20,bgcolor=ft.Colors.WHITE,border_radius=18,
                shadow=ft.BoxShadow(blur_radius=12,color=ft.Colors.BLACK12,offset=ft.Offset(0,3)),
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.FLAG,color=ft.Colors.BLUE_600,size=22),
                        ft.Text("Progreso por País",size=17,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_GREY_800),
                        ft.Container(expand=True),
                        ft.Text(f"{pc} completos ✓",size=12,color=ft.Colors.GREEN_600,weight=ft.FontWeight.BOLD)],spacing=8),
                    ft.Divider(height=6,color=ft.Colors.GREY_100),
                    ft.Column(filas,spacing=6,scroll=ft.ScrollMode.AUTO),
                ],spacing=10)),
        ],spacing=10,scroll=ft.ScrollMode.AUTO))

    # ── VISTA ÁLBUM ─────────────────────────────────────────────────
    def vista_album():
        def tc2(label,widget,color,icono):
            return ft.Container(expand=True,padding=14,border_radius=14,bgcolor=ft.Colors.WHITE,
                border=ft.Border.all(1,ft.Colors.GREY_200),
                shadow=ft.BoxShadow(blur_radius=6,color=ft.Colors.BLACK12,offset=ft.Offset(0,2)),
                content=ft.Column([ft.Icon(icono,color=color,size=22),widget,
                    ft.Text(label,size=11,color=ft.Colors.GREY_500,text_align=ft.TextAlign.CENTER)],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=3))
        cnt=ft.Row([tc2("Tengo",txt_t,"#10B981",ft.Icons.CHECK_CIRCLE),
            tc2("Faltan",txt_f,ft.Colors.ORANGE_600,ft.Icons.HELP_OUTLINE),
            tc2("Repetidas",txt_r,ft.Colors.BLUE_400,ft.Icons.COPY_ALL)],spacing=10)
        def chip(color,texto):
            return ft.Row([ft.Container(width=13,height=13,bgcolor=color,border_radius=4),
                ft.Text(texto,size=12,color=ft.Colors.BLUE_GREY_700)],spacing=5)
        leyenda=ft.Row([chip(C_FALTA,"Falta"),chip(C_TENGO,"Tengo (1 clic)"),chip(C_REPETIDA,"Repetida (2 clics)")],spacing=14)
        dd=ft.Dropdown(label="Selección Nacional",value=pais_sel[0],
            options=[ft.dropdown.Option(key=c,text=f"[{iso}]  {n}") for c,n,iso in PAISES],
            width=320,border_radius=10,bgcolor=ft.Colors.WHITE,on_select=on_pais,
            border_color=ft.Colors.with_opacity(0.3,"#2563EB"),
            focused_border_color="#F59E0B",label_style=ft.TextStyle(color="#1A3A6B"))
        def reset(e):
            p=pais_sel[0];nm,_=PAISES_DICT.get(p,(p,""))
            for i in range(1,21): album.pop(f"{p}{i}",None)
            guardar(album);upd_tablero(p);page.update()
            snk(f"🔄 {nm} reiniciado",ft.Colors.ORANGE_700)
        btn_reset=ft.Button(content=ft.Row([ft.Icon(ft.Icons.REFRESH,color=ft.Colors.WHITE),
            ft.Text("Reiniciar País",color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD,size=13)],tight=True,spacing=6),
            on_click=reset,style=ft.ButtonStyle(bgcolor="#EF4444",color=ft.Colors.WHITE,
                padding=ft.Padding(16,12,16,12),shape=ft.RoundedRectangleBorder(radius=12),elevation=3))
        btn_bus=ft.Button(content=ft.Row([ft.Icon(ft.Icons.SEARCH,color="#0D1B3E"),
            ft.Text("Buscar Intercambio",color="#0D1B3E",weight=ft.FontWeight.BOLD,size=15)],tight=True,spacing=8),
            on_click=buscar,style=ft.ButtonStyle(bgcolor="#F59E0B",color="#0D1B3E",
                padding=ft.Padding(24,14,24,14),shape=ft.RoundedRectangleBorder(radius=12),elevation=6))
        btn_save=ft.Button(content=ft.Row([ft.Icon(ft.Icons.SAVE,color=ft.Colors.WHITE),
            ft.Text("Guardar",color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD,size=15)],tight=True,spacing=8),
            on_click=lambda e:snk("✅ Guardado") if guardar(album) else snk("❌ Error",ft.Colors.RED_700),
            style=ft.ButtonStyle(bgcolor="#2563EB",color=ft.Colors.WHITE,
                padding=ft.Padding(24,14,24,14),shape=ft.RoundedRectangleBorder(radius=12),elevation=4))
        return ft.Container(padding=ft.Padding(20,16,20,24),content=ft.Column([
            cnt,ft.Divider(height=6,color=ft.Colors.TRANSPARENT),
            ft.Container(padding=20,bgcolor="#FFFFFF",border_radius=18,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.1, "#2563EB")),
                shadow=ft.BoxShadow(blur_radius=16,color=ft.Colors.with_opacity(0.12,"#0D1B3E"),offset=ft.Offset(0,4)),
                content=ft.Column([
                    ft.Row([
                        ft.Container(width=32,height=32,border_radius=8,bgcolor="#2563EB",
                            alignment=ft.Alignment(0,0),
                            content=ft.Icon(ft.Icons.GRID_VIEW,color=ft.Colors.WHITE,size=18)),
                        ft.Text("Mi Álbum",size=17,weight=ft.FontWeight.BOLD,color="#0D1B3E"),
                        ft.Container(expand=True),
                        ft.Row([ft.Icon(ft.Icons.CLOUD_DONE,color="#10B981",size=16),
                            ft.Text("Auto-guardado",size=11,color="#10B981")],spacing=4)],spacing=8),
                    leyenda,ft.Divider(height=8,color=ft.Colors.GREY_100),
                    ft.Row([dd,ft.Container(expand=True),btn_reset],spacing=8),
                    ft.Column([ft.Row([
                        ft.Text("Progreso",size=12,color="#1A3A6B",weight=ft.FontWeight.BOLD),
                        txt_prog],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),barra],spacing=5),
                    ft.Container(content=grid_c,padding=ft.Padding(0,6,0,0)),
                ],spacing=12)),
            ft.Divider(height=10,color=ft.Colors.TRANSPARENT),
            ft.Row([btn_bus,btn_save],alignment=ft.MainAxisAlignment.CENTER,spacing=12),
            ft.Divider(height=10,color=ft.Colors.TRANSPARENT),
            ft.Row([
                ft.Container(width=28,height=28,border_radius=8,
                    gradient=ft.LinearGradient(colors=["#F59E0B","#FCD34D"]),
                    alignment=ft.Alignment(0,0),
                    content=ft.Icon(ft.Icons.SWAP_HORIZ,color="#0D1B3E",size=16)),
                ft.Text("Intercambios Sugeridos",size=17,weight=ft.FontWeight.BOLD,color="#0D1B3E")],spacing=8),
            resultados,
        ],spacing=10))


    # ── VISTA ESPECIALES ─────────────────────────────────────────────
    def vista_especiales():
        ARCHIVO_ESP = "especiales_guardado.json"

        def cargar_esp():
            if os.path.exists(ARCHIVO_ESP):
                try:
                    with open(ARCHIVO_ESP,"r",encoding="utf-8") as f: return json.load(f)
                except: pass
            return {}

        def guardar_esp(data):
            try:
                with open(ARCHIVO_ESP,"w",encoding="utf-8") as f:
                    json.dump(data,f,ensure_ascii=False,indent=2)
            except: pass

        mis_esp = cargar_esp()
        categoria_sel = [list(ESPECIALES.keys())[0]]
        resultados_esp = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO)
        grid_esp = ft.Column([], spacing=6)
        estado_busq = ft.Text("", size=13, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)

        FALTA_ESP="falta"; TENGO_ESP="tengo"; REPETIDA_ESP="repetida"

        def estilo_esp(estado):
            if estado==TENGO_ESP: return ft.Colors.GREEN_500, ft.Colors.WHITE
            if estado==REPETIDA_ESP: return ft.Colors.BLUE_400, ft.Colors.WHITE
            return ft.Colors.GREY_100, ft.Colors.BLUE_GREY_600

        def actualizar_grid_esp(cat_key):
            grid_esp.controls.clear()
            cat = ESPECIALES[cat_key]
            col = COLORES_ESPECIALES[cat["color"]]
            for est in cat["estampas"]:
                eid = est["id"]
                estado = mis_esp.get(eid, FALTA_ESP)
                bg, fg = estilo_esp(estado)

                def make_tap(eid=eid):
                    def on_tap(e):
                        prev = mis_esp.get(eid, FALTA_ESP)
                        mis_esp[eid] = TENGO_ESP if prev == FALTA_ESP else FALTA_ESP
                        guardar_esp(mis_esp)
                        actualizar_grid_esp(categoria_sel[0])
                        try: grid_esp.update()
                        except: pass
                    return on_tap

                def make_dtap(eid=eid):
                    def on_dtap(e):
                        mis_esp[eid] = REPETIDA_ESP
                        guardar_esp(mis_esp)
                        actualizar_grid_esp(categoria_sel[0])
                        try: grid_esp.update()
                        except: pass
                    return on_dtap

                bg_actual, fg_actual = estilo_esp(mis_esp.get(eid, FALTA_ESP))
                
                # Badge de tipo
                tipo_color = ft.Colors.AMBER_600
                if "Negro" in est["tipo"]: tipo_color = ft.Colors.GREY_900
                elif "Crumple" in est["tipo"]: tipo_color = ft.Colors.ORANGE_600
                elif "Coca" in est["tipo"]: tipo_color = ft.Colors.RED_600
                elif "Museum" in est["tipo"]: tipo_color = ft.Colors.PURPLE_600
                elif "Parallel" in est["tipo"]: tipo_color = ft.Colors.BLUE_600

                grid_esp.controls.append(
                    ft.GestureDetector(
                        on_tap=make_tap(),
                        on_double_tap=make_dtap(),
                        content=ft.Container(
                            padding=ft.Padding(12,10,12,10),
                            border_radius=12,
                            bgcolor=bg_actual,
                            border=ft.Border.all(1.5, col["border"] if bg_actual==ft.Colors.GREY_100 else ft.Colors.TRANSPARENT),
                            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.BLACK12, offset=ft.Offset(0,2)) if bg_actual!=ft.Colors.GREY_100 else None,
                            content=ft.Row([
                                ft.Column([
                                    ft.Text(est["jugador"], size=14, weight=ft.FontWeight.BOLD, color=fg_actual),
                                    ft.Text(est["pais"], size=12, color=fg_actual if bg_actual!=ft.Colors.GREY_100 else ft.Colors.GREY_500),
                                    ft.Container(
                                        padding=ft.Padding(6,2,6,2), border_radius=20,
                                        bgcolor=tipo_color,
                                        content=ft.Text(est["tipo"], size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                    ),
                                ], spacing=3, expand=True),
                                ft.Text(
                                    "✓ Tengo" if bg_actual==ft.Colors.GREEN_500
                                    else "🔄 Repetida" if bg_actual==ft.Colors.BLUE_400
                                    else "❌ Falta",
                                    size=11, color=fg_actual if bg_actual!=ft.Colors.GREY_100 else ft.Colors.GREY_400,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        )
                    )
                )

        def buscar_esp(e):
            resultados_esp.controls.clear()
            mis_rep_esp = {k for k,v in mis_esp.items() if v==REPETIDA_ESP}
            mis_fal_esp = {k for k,v in mis_esp.items() if v==FALTA_ESP}
            # También incluir las que no están marcadas
            for cat in ESPECIALES.values():
                for est in cat["estampas"]:
                    if est["id"] not in mis_esp:
                        mis_fal_esp.add(est["id"])

            if not mis_rep_esp:
                estado_busq.value = "⚠️ Marca estampas como Repetidas (doble clic) para buscar intercambios"
                estado_busq.color = ft.Colors.ORANGE_700
                try: estado_busq.update()
                except: pass
                return

            # Buscar en usuarios_db
            enc = 0
            if os.path.exists("usuarios_db.json"):
                try:
                    db = json.load(open("usuarios_db.json","r",encoding="utf-8"))
                    for uid, u in db.items():
                        if uid == MI_ID: continue
                        sus_rep = set(u.get("repetidas_esp",[]))
                        sus_fal = set(u.get("faltantes_esp",[]))
                        me_da  = sus_rep & mis_fal_esp
                        le_doy = mis_rep_esp & sus_fal
                        if me_da or le_doy:
                            resultados_esp.controls.append(
                                ft.Card(elevation=3, content=ft.Container(
                                    padding=16, border_radius=14, bgcolor=ft.Colors.WHITE,
                                    border=ft.Border.all(1.5, ft.Colors.AMBER_300),
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER_600, size=20),
                                            ft.Text(u["nombre"], weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.BLUE_GREY_900),
                                        ], spacing=8),
                                        ft.Divider(height=8, color=ft.Colors.GREY_100),
                                        ft.Container(bgcolor=ft.Colors.GREEN_50, border_radius=8, padding=ft.Padding(8,6,8,6),
                                            content=ft.Text(f"⭐ Te da: {', '.join(sorted(me_da)) if me_da else 'Ninguna'}", size=13, color=ft.Colors.GREEN_800)),
                                        ft.Container(bgcolor=ft.Colors.BLUE_50, border_radius=8, padding=ft.Padding(8,6,8,6),
                                            content=ft.Text(f"🔄 Tú le das: {', '.join(sorted(le_doy)) if le_doy else 'Ninguna'}", size=13, color=ft.Colors.BLUE_800)),
                                    ], spacing=8)
                                ))
                            )
                            enc += 1
                except: pass

            if enc == 0:
                resultados_esp.controls.append(
                    ft.Container(alignment=ft.Alignment(0,0), padding=20,
                        content=ft.Column([
                            ft.Text("😔", size=36),
                            ft.Text("No hay intercambios de especiales disponibles",
                                color=ft.Colors.GREY_500, italic=True, text_align=ft.TextAlign.CENTER, size=13),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6))
                )

            estado_busq.value = f"✅ Búsqueda completa"
            estado_busq.color = ft.Colors.GREEN_700
            try: resultados_esp.update(); estado_busq.update(); page.update()
            except: pass

        # Tabs de categorías
        def chip_cat(cat_key, cat_data):
            col = COLORES_ESPECIALES[cat_data["color"]]
            def on_click(e, k=cat_key):
                categoria_sel[0] = k
                actualizar_grid_esp(k)
                try: grid_esp.update(); page.update()
                except: pass

            total = len(cat_data["estampas"])
            tengo = sum(1 for e in cat_data["estampas"] if mis_esp.get(e["id"]) in (TENGO_ESP, REPETIDA_ESP))

            return ft.GestureDetector(
                on_tap=on_click,
                content=ft.Container(
                    padding=ft.Padding(12, 8, 12, 8),
                    border_radius=20,
                    bgcolor=col["header"],
                    content=ft.Column([
                        ft.Text(cat_data["nombre"], size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{tengo}/{total}", size=11, color=ft.Colors.WHITE70),
                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                )
            )

        chips = ft.Row([chip_cat(k,v) for k,v in ESPECIALES.items()], spacing=8, scroll=ft.ScrollMode.AUTO)

        # Stats rápidas
        total_esp = sum(len(v["estampas"]) for v in ESPECIALES.values())
        tengo_esp = sum(1 for v in mis_esp.values() if v in (TENGO_ESP, REPETIDA_ESP))
        rep_esp   = sum(1 for v in mis_esp.values() if v == REPETIDA_ESP)

        btn_buscar_esp = ft.Button(
            content=ft.Row([ft.Icon(ft.Icons.SEARCH, color=ft.Colors.WHITE),
                ft.Text("Buscar Intercambio de Especiales", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)],
                tight=True, spacing=8),
            on_click=buscar_esp,
            style=ft.ButtonStyle(bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE,
                padding=ft.Padding(20,12,20,12), shape=ft.RoundedRectangleBorder(radius=12), elevation=4),
        )

        # Init grid
        actualizar_grid_esp(categoria_sel[0])

        return ft.Container(padding=ft.Padding(20,16,20,24), content=ft.Column([
            # Stats header
            ft.Row([
                ft.Container(expand=True, padding=14, border_radius=14, bgcolor=ft.Colors.WHITE,
                    border=ft.Border.all(1,ft.Colors.AMBER_200),
                    shadow=ft.BoxShadow(blur_radius=6,color=ft.Colors.BLACK12,offset=ft.Offset(0,2)),
                    content=ft.Column([ft.Icon(ft.Icons.STAR,color=ft.Colors.AMBER_600,size=22),
                        ft.Text(str(tengo_esp),size=24,weight=ft.FontWeight.BOLD,color=ft.Colors.AMBER_700),
                        ft.Text(f"de {total_esp} especiales",size=11,color=ft.Colors.GREY_500,text_align=ft.TextAlign.CENTER)],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=3)),
                ft.Container(expand=True, padding=14, border_radius=14, bgcolor=ft.Colors.WHITE,
                    border=ft.Border.all(1,ft.Colors.BLUE_200),
                    shadow=ft.BoxShadow(blur_radius=6,color=ft.Colors.BLACK12,offset=ft.Offset(0,2)),
                    content=ft.Column([ft.Icon(ft.Icons.SWAP_HORIZ,color=ft.Colors.BLUE_600,size=22),
                        ft.Text(str(rep_esp),size=24,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_600),
                        ft.Text("Repetidas para intercambio",size=11,color=ft.Colors.GREY_500,text_align=ft.TextAlign.CENTER)],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=3)),
                ft.Container(expand=True, padding=14, border_radius=14, bgcolor=ft.Colors.WHITE,
                    border=ft.Border.all(1,ft.Colors.GREY_200),
                    shadow=ft.BoxShadow(blur_radius=6,color=ft.Colors.BLACK12,offset=ft.Offset(0,2)),
                    content=ft.Column([ft.Icon(ft.Icons.HELP_OUTLINE,color=ft.Colors.ORANGE_600,size=22),
                        ft.Text(str(total_esp-tengo_esp),size=24,weight=ft.FontWeight.BOLD,color=ft.Colors.ORANGE_600),
                        ft.Text("Faltan",size=11,color=ft.Colors.GREY_500,text_align=ft.TextAlign.CENTER)],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=3)),
            ], spacing=10),

            # Álbum especiales
            ft.Container(padding=20, bgcolor=ft.Colors.WHITE, border_radius=18,
                shadow=ft.BoxShadow(blur_radius=12,color=ft.Colors.BLACK12,offset=ft.Offset(0,3)),
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER_600, size=22),
                        ft.Text("Estampas Especiales", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
                    ], spacing=8),
                    ft.Container(
                        padding=10, border_radius=10, bgcolor=ft.Colors.AMBER_50,
                        border=ft.Border.all(1,ft.Colors.AMBER_200),
                        content=ft.Row([
                            ft.Icon(ft.Icons.TOUCH_APP, color=ft.Colors.AMBER_700, size=16),
                            ft.Text("1 clic = Tengo  |  Doble clic = Repetida (para intercambio)",
                                size=12, color=ft.Colors.AMBER_800),
                        ], spacing=6),
                    ),
                    ft.Divider(height=8, color=ft.Colors.GREY_100),
                    ft.Text("Categoría:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_700),
                    chips,
                    ft.Divider(height=6, color=ft.Colors.GREY_100),
                    grid_esp,
                ], spacing=10)),

            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Row([btn_buscar_esp], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([estado_busq], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=6, color=ft.Colors.TRANSPARENT),

            ft.Row([
                ft.Icon(ft.Icons.SWAP_HORIZ, color=ft.Colors.AMBER_600, size=20),
                ft.Text("Intercambios de Especiales", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
            ], spacing=8),
            resultados_esp,
        ], spacing=10, scroll=ft.ScrollMode.AUTO))


    # ── VISTA REPUTACIÓN ─────────────────────────────────────────────
    def vista_reputacion():
        rep_db   = cargar_json(ARCHIVO_REPUTACION)
        mi_rep   = rep_db.get(MI_ID, {"nombre": nombre_u[0], "estrellas": [], "resenas": [], "intercambios": 0})
        lista_res = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO)
        cal_resultado = ft.Text("", size=13, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)

        def promedio(estrellas):
            return round(sum(estrellas)/len(estrellas),1) if estrellas else 0.0

        def estrellas_widget(n, size=20, color=ft.Colors.AMBER_500):
            return ft.Row([
                ft.Icon(ft.Icons.STAR if i < int(n) else
                       (ft.Icons.STAR_HALF if i < n else ft.Icons.STAR_BORDER),
                       color=color, size=size)
                for i in range(5)
            ], spacing=2)

        def cargar_lista():
            lista_res.controls.clear()
            resenas = mi_rep.get("resenas", [])
            if not resenas:
                lista_res.controls.append(
                    ft.Container(alignment=ft.Alignment(0,0), padding=20,
                        content=ft.Column([
                            ft.Text("⭐", size=36),
                            ft.Text("Aún no tienes reseñas", color=ft.Colors.GREY_500,
                                italic=True, text_align=ft.TextAlign.CENTER, size=13),
                            ft.Text("Completa intercambios para recibir calificaciones",
                                color=ft.Colors.GREY_400, size=12, text_align=ft.TextAlign.CENTER),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6))
                )
            else:
                for r in resenas[:10]:
                    lista_res.controls.append(
                        ft.Container(padding=14, border_radius=12, bgcolor=ft.Colors.WHITE,
                            border=ft.Border.all(1, ft.Colors.GREY_200),
                            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.BLACK12, offset=ft.Offset(0,2)),
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_400, size=18),
                                    ft.Text(r.get("de","Anónimo"), size=13, weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLUE_GREY_800),
                                    ft.Container(expand=True),
                                    estrellas_widget(r.get("estrellas",5), size=14),
                                    ft.Text(r.get("fecha",""), size=11, color=ft.Colors.GREY_500),
                                ], spacing=6),
                                ft.Text(r.get("comentario",""), size=12, color=ft.Colors.BLUE_GREY_600,
                                    italic=True) if r.get("comentario") else ft.Container(),
                            ], spacing=4))
                    )
            try: lista_res.update()
            except: pass

        # Calificar a otro usuario
        sel_estrellas = [5]
        campo_calif_nombre = ft.TextField(label="Nombre del usuario a calificar",
            width=240, border_radius=10, bgcolor=ft.Colors.WHITE)
        campo_comentario = ft.TextField(label="Comentario (opcional)", width=360,
            border_radius=10, bgcolor=ft.Colors.WHITE, multiline=True, max_lines=2)

        def star_buttons():
            row = ft.Row(spacing=4)
            def make_click(n):
                def click(e):
                    sel_estrellas[0] = n
                    for i, btn in enumerate(row.controls):
                        btn.icon_color = ft.Colors.AMBER_500 if i < n else ft.Colors.GREY_300
                        btn.update()
                    cal_resultado.value = f"{'⭐'*n} Seleccionado"
                    cal_resultado.color = ft.Colors.AMBER_600
                    try: cal_resultado.update()
                    except: pass
                return click
            for i in range(5):
                row.controls.append(ft.IconButton(
                    icon=ft.Icons.STAR,
                    icon_color=ft.Colors.AMBER_500 if i < 5 else ft.Colors.GREY_300,
                    icon_size=32,
                    on_click=make_click(i+1),
                ))
            return row

        def enviar_calificacion(e):
            nombre_otro = campo_calif_nombre.value.strip()
            if not nombre_otro:
                cal_resultado.value = "⚠️ Escribe el nombre del usuario"
                cal_resultado.color = ft.Colors.ORANGE_700
                try: cal_resultado.update()
                except: pass
                return
            from datetime import datetime
            db = cargar_json(ARCHIVO_REPUTACION)
            # Buscar usuario por nombre en db
            uid_destino = None
            for uid, u in db.items():
                if u.get("nombre","").lower() == nombre_otro.lower():
                    uid_destino = uid
                    break
            if not uid_destino:
                uid_destino = f"user_{nombre_otro.replace(' ','_')}"
                db[uid_destino] = {"nombre": nombre_otro, "estrellas":[], "resenas":[], "intercambios":0}

            nueva_resena = {
                "de": nombre_u[0],
                "estrellas": sel_estrellas[0],
                "comentario": campo_comentario.value.strip(),
                "fecha": datetime.now().strftime("%d/%m/%Y"),
            }
            db[uid_destino]["estrellas"].append(sel_estrellas[0])
            db[uid_destino]["resenas"].insert(0, nueva_resena)
            guardar_json(ARCHIVO_REPUTACION, db)

            agregar_notificacion(
                f"⭐ Calificaste a {nombre_otro} con {'⭐'*sel_estrellas[0]}",
                "reputacion"
            )
            try: actualizar_badge_notif()
            except: pass

            cal_resultado.value = f"✅ ¡Calificación enviada a {nombre_otro}!"
            cal_resultado.color = ft.Colors.GREEN_700
            campo_calif_nombre.value = ""
            campo_comentario.value = ""
            try: cal_resultado.update(); campo_calif_nombre.update(); campo_comentario.update()
            except: pass

        prom = promedio(mi_rep.get("estrellas", []))
        total_interc = mi_rep.get("intercambios", 0)
        total_resenas = len(mi_rep.get("resenas", []))

        nivel = "🥉 Principiante"
        color_nivel = ft.Colors.BROWN_400
        if total_interc >= 50: nivel="🏆 Maestro"; color_nivel=ft.Colors.AMBER_600
        elif total_interc >= 20: nivel="🥇 Experto"; color_nivel=ft.Colors.YELLOW_700
        elif total_interc >= 10: nivel="🥈 Avanzado"; color_nivel=ft.Colors.GREY_500
        elif total_interc >= 5:  nivel="🎖️ Intermedio"; color_nivel=ft.Colors.BLUE_400

        cargar_lista()
        stars = star_buttons()

        return ft.Container(padding=ft.Padding(20,16,20,24), content=ft.Column([
            # Mi perfil
            ft.Container(padding=20, bgcolor=ft.Colors.WHITE, border_radius=18,
                shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK12, offset=ft.Offset(0,3)),
                content=ft.Column([
                    ft.Row([
                        ft.Container(width=60, height=60, border_radius=30,
                            bgcolor=ft.Colors.BLUE_600,
                            alignment=ft.Alignment(0,0),
                            content=ft.Text(nombre_u[0][0].upper() if nombre_u[0] else "?",
                                size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)),
                        ft.Column([
                            ft.Text(nombre_u[0], size=18, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_GREY_900),
                            ft.Container(padding=ft.Padding(8,4,8,4), border_radius=20,
                                bgcolor=color_nivel,
                                content=ft.Text(nivel, size=12, color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD)),
                        ], spacing=6, expand=True),
                    ], spacing=16),
                    ft.Divider(height=12, color=ft.Colors.GREY_100),
                    ft.Row([
                        ft.Column([
                            estrellas_widget(prom, size=22),
                            ft.Text(f"{prom}/5.0", size=20, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.AMBER_600),
                            ft.Text("Calificación", size=11, color=ft.Colors.GREY_500),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, expand=True),
                        ft.VerticalDivider(width=1, color=ft.Colors.GREY_200),
                        ft.Column([
                            ft.Icon(ft.Icons.SWAP_HORIZ, color=ft.Colors.BLUE_600, size=26),
                            ft.Text(str(total_interc), size=20, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_600),
                            ft.Text("Intercambios", size=11, color=ft.Colors.GREY_500),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, expand=True),
                        ft.VerticalDivider(width=1, color=ft.Colors.GREY_200),
                        ft.Column([
                            ft.Icon(ft.Icons.RATE_REVIEW, color=ft.Colors.GREEN_600, size=26),
                            ft.Text(str(total_resenas), size=20, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_600),
                            ft.Text("Reseñas", size=11, color=ft.Colors.GREY_500),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, expand=True),
                    ], spacing=10),
                ], spacing=12)),

            ft.Divider(height=8, color=ft.Colors.TRANSPARENT),

            # Calificar a otro
            ft.Container(padding=20, bgcolor=ft.Colors.WHITE, border_radius=18,
                shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK12, offset=ft.Offset(0,3)),
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER_600, size=22),
                        ft.Text("Calificar a otro usuario", size=17, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_GREY_800)], spacing=8),
                    ft.Text("Después de un intercambio, califica al otro coleccionista:",
                        size=12, color=ft.Colors.GREY_500),
                    ft.Divider(height=6, color=ft.Colors.GREY_100),
                    campo_calif_nombre,
                    ft.Text("Selecciona estrellas:", size=13, color=ft.Colors.BLUE_GREY_700),
                    stars,
                    campo_comentario,
                    ft.Button(
                        content=ft.Row([ft.Icon(ft.Icons.SEND, color=ft.Colors.WHITE),
                            ft.Text("Enviar Calificación", color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD)], tight=True, spacing=8),
                        on_click=enviar_calificacion,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.AMBER_600, color=ft.Colors.WHITE,
                            padding=ft.Padding(20,12,20,12),
                            shape=ft.RoundedRectangleBorder(radius=12), elevation=4),
                    ),
                    ft.Row([cal_resultado], alignment=ft.MainAxisAlignment.CENTER),
                ], spacing=10)),

            ft.Divider(height=8, color=ft.Colors.TRANSPARENT),

            # Mis reseñas
            ft.Container(padding=20, bgcolor=ft.Colors.WHITE, border_radius=18,
                shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK12, offset=ft.Offset(0,3)),
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.RATE_REVIEW, color=ft.Colors.BLUE_600, size=22),
                        ft.Text("Mis Reseñas", size=17, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_GREY_800)], spacing=8),
                    lista_res,
                ], spacing=10)),
        ], spacing=10, scroll=ft.ScrollMode.AUTO))

    # ── VISTA EVENTOS ────────────────────────────────────────────────
    def vista_eventos():
        from datetime import datetime
        eventos_lista = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
        msg_evento = ft.Text("", size=13, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)

        campo_ev_nombre  = ft.TextField(label="Nombre del evento", width=340, border_radius=10, bgcolor=ft.Colors.WHITE)
        campo_ev_lugar   = ft.TextField(label="Lugar (ej: Starbucks Misiones)", width=340, border_radius=10, bgcolor=ft.Colors.WHITE)
        campo_ev_fecha   = ft.TextField(label="Fecha (ej: Sábado 25 Jun, 3:00 PM)", width=340, border_radius=10, bgcolor=ft.Colors.WHITE)
        campo_ev_desc    = ft.TextField(label="Descripción (opcional)", width=340, border_radius=10,
            bgcolor=ft.Colors.WHITE, multiline=True, max_lines=2)

        def cargar_eventos():
            eventos_lista.controls.clear()
            db = cargar_json(ARCHIVO_EVENTOS)
            eventos = list(db.values())
            eventos.sort(key=lambda x: x.get("fecha_creacion",""), reverse=True)

            if not eventos:
                eventos_lista.controls.append(
                    ft.Container(alignment=ft.Alignment(0,0), padding=30,
                        content=ft.Column([
                            ft.Text("📅", size=40),
                            ft.Text("No hay eventos aún", color=ft.Colors.GREY_500,
                                italic=True, text_align=ft.TextAlign.CENTER, size=14),
                            ft.Text("¡Crea el primero!",
                                color=ft.Colors.GREY_400, size=12, text_align=ft.TextAlign.CENTER),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8))
                )
            else:
                for ev in eventos:
                    confirmados = ev.get("confirmados", [])
                    ya_confirme = nombre_u[0] in confirmados
                    es_mio = ev.get("creador") == nombre_u[0]

                    def make_confirmar(ev_id=ev.get("id",""), ev_nombre=ev.get("nombre","")):
                        def confirmar(e):
                            db2 = cargar_json(ARCHIVO_EVENTOS)
                            if ev_id in db2:
                                if nombre_u[0] not in db2[ev_id]["confirmados"]:
                                    db2[ev_id]["confirmados"].append(nombre_u[0])
                                    guardar_json(ARCHIVO_EVENTOS, db2)
                                    agregar_notificacion(f"📅 Te uniste al evento: {ev_nombre}", "evento")
                                    try: actualizar_badge_notif()
                                    except: pass
                                    cargar_eventos()
                                    try: eventos_lista.update(); page.update()
                                    except: pass
                        return confirmar

                    def make_cancelar(ev_id=ev.get("id","")):
                        def cancelar(e):
                            db2 = cargar_json(ARCHIVO_EVENTOS)
                            if ev_id in db2:
                                db2[ev_id]["confirmados"] = [
                                    u for u in db2[ev_id]["confirmados"] if u != nombre_u[0]
                                ]
                                guardar_json(ARCHIVO_EVENTOS, db2)
                                cargar_eventos()
                                try: eventos_lista.update(); page.update()
                                except: pass
                        return cancelar

                    def make_eliminar(ev_id=ev.get("id","")):
                        def eliminar(e):
                            db2 = cargar_json(ARCHIVO_EVENTOS)
                            if ev_id in db2:
                                del db2[ev_id]
                                guardar_json(ARCHIVO_EVENTOS, db2)
                                cargar_eventos()
                                try: eventos_lista.update(); page.update()
                                except: pass
                        return eliminar

                    eventos_lista.controls.append(
                        ft.Card(elevation=3, content=ft.Container(
                            padding=16, border_radius=16, bgcolor=ft.Colors.WHITE,
                            border=ft.Border.all(1.5,
                                ft.Colors.BLUE_300 if ya_confirme else ft.Colors.GREY_200),
                            content=ft.Column([
                                ft.Row([
                                    ft.Container(
                                        padding=ft.Padding(10,8,10,8), border_radius=12,
                                        bgcolor=ft.Colors.BLUE_600,
                                        content=ft.Text("📅", size=22),
                                    ),
                                    ft.Column([
                                        ft.Text(ev.get("nombre","Sin nombre"), size=15,
                                            weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                                        ft.Row([
                                            ft.Icon(ft.Icons.LOCATION_ON, size=13, color=ft.Colors.GREY_500),
                                            ft.Text(ev.get("lugar","?"), size=12, color=ft.Colors.GREY_600),
                                        ], spacing=3),
                                        ft.Row([
                                            ft.Icon(ft.Icons.ACCESS_TIME, size=13, color=ft.Colors.GREY_500),
                                            ft.Text(ev.get("fecha","?"), size=12, color=ft.Colors.GREY_600),
                                        ], spacing=3),
                                    ], spacing=2, expand=True),
                                ], spacing=12),
                                ft.Text(ev.get("descripcion",""), size=12, color=ft.Colors.GREY_500,
                                    italic=True) if ev.get("descripcion") else ft.Container(),
                                ft.Divider(height=8, color=ft.Colors.GREY_100),
                                ft.Row([
                                    ft.Container(
                                        padding=ft.Padding(8,4,8,4), border_radius=20,
                                        bgcolor=ft.Colors.GREEN_50,
                                        border=ft.Border.all(1, ft.Colors.GREEN_200),
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.GREEN_700, size=14),
                                            ft.Text(f"{len(confirmados)} confirmados",
                                                size=12, color=ft.Colors.GREEN_700, weight=ft.FontWeight.BOLD),
                                        ], spacing=4),
                                    ),
                                    ft.Text(f"Por: {ev.get('creador','?')}", size=11,
                                        color=ft.Colors.GREY_400),
                                    ft.Container(expand=True),
                                    ft.Button(
                                        content=ft.Text("✓ Confirmado" if ya_confirme else "Unirme",
                                            color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=12),
                                        on_click=make_cancelar(ev.get("id","")) if ya_confirme
                                                 else make_confirmar(ev.get("id",""), ev.get("nombre","")),
                                        style=ft.ButtonStyle(
                                            bgcolor=ft.Colors.GREY_400 if ya_confirme else ft.Colors.BLUE_600,
                                            color=ft.Colors.WHITE,
                                            padding=ft.Padding(14,8,14,8),
                                            shape=ft.RoundedRectangleBorder(radius=20)),
                                    ),
                                    ft.IconButton(ft.Icons.DELETE_OUTLINE,
                                        icon_color=ft.Colors.RED_300, icon_size=18,
                                        on_click=make_eliminar(ev.get("id","")),
                                        visible=es_mio,
                                    ) if es_mio else ft.Container(),
                                ], spacing=8, alignment=ft.MainAxisAlignment.START,
                                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                # Confirmados list
                                ft.Text(f"👥 {', '.join(confirmados)}" if confirmados else "",
                                    size=11, color=ft.Colors.GREY_500) if confirmados else ft.Container(),
                            ], spacing=8)))
                    )
            try: eventos_lista.update()
            except: pass

        def crear_evento(e):
            if not campo_ev_nombre.value.strip() or not campo_ev_lugar.value.strip():
                msg_evento.value = "⚠️ Nombre y lugar son obligatorios"
                msg_evento.color = ft.Colors.ORANGE_700
                try: msg_evento.update()
                except: pass
                return
            import uuid as _uuid
            from datetime import datetime
            ev_id = str(_uuid.uuid4())[:8]
            db = cargar_json(ARCHIVO_EVENTOS)
            db[ev_id] = {
                "id": ev_id,
                "nombre": campo_ev_nombre.value.strip(),
                "lugar": campo_ev_lugar.value.strip(),
                "fecha": campo_ev_fecha.value.strip() or "Por definir",
                "descripcion": campo_ev_desc.value.strip(),
                "creador": nombre_u[0],
                "confirmados": [nombre_u[0]],
                "fecha_creacion": datetime.now().isoformat(),
            }
            guardar_json(ARCHIVO_EVENTOS, db)
            agregar_notificacion(f"📅 Creaste el evento: {campo_ev_nombre.value.strip()}", "evento")
            try: actualizar_badge_notif()
            except: pass
            campo_ev_nombre.value = ""
            campo_ev_lugar.value = ""
            campo_ev_fecha.value = ""
            campo_ev_desc.value = ""
            msg_evento.value = "✅ ¡Evento creado!"
            msg_evento.color = ft.Colors.GREEN_700
            cargar_eventos()
            try:
                msg_evento.update(); campo_ev_nombre.update()
                campo_ev_lugar.update(); campo_ev_fecha.update()
                campo_ev_desc.update(); eventos_lista.update(); page.update()
            except: pass

        cargar_eventos()

        return ft.Container(padding=ft.Padding(20,16,20,24), content=ft.Column([
            # Crear evento
            ft.Container(padding=20, bgcolor=ft.Colors.WHITE, border_radius=18,
                shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK12, offset=ft.Offset(0,3)),
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.ADD_CIRCLE, color=ft.Colors.BLUE_600, size=22),
                        ft.Text("Crear Evento de Intercambio", size=17, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_GREY_800)], spacing=8),
                    ft.Text("Organiza un encuentro grupal para intercambiar estampas",
                        size=12, color=ft.Colors.GREY_500),
                    ft.Divider(height=6, color=ft.Colors.GREY_100),
                    campo_ev_nombre, campo_ev_lugar, campo_ev_fecha, campo_ev_desc,
                    ft.Button(
                        content=ft.Row([ft.Icon(ft.Icons.EVENT, color=ft.Colors.WHITE),
                            ft.Text("Crear Evento", color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD)], tight=True, spacing=8),
                        on_click=crear_evento,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE,
                            padding=ft.Padding(20,12,20,12),
                            shape=ft.RoundedRectangleBorder(radius=12), elevation=4),
                    ),
                    ft.Row([msg_evento], alignment=ft.MainAxisAlignment.CENTER),
                ], spacing=10)),
            ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
            # Lista eventos
            ft.Row([ft.Icon(ft.Icons.EVENT_NOTE, color=ft.Colors.BLUE_600, size=22),
                ft.Text("Eventos Disponibles", size=17, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_GREY_800)], spacing=8),
            eventos_lista,
        ], spacing=10, scroll=ft.ScrollMode.AUTO))

    # ── VISTA NOTIFICACIONES ──────────────────────────────────────────
    def vista_notificaciones():
        notifs_db = cargar_json(ARCHIVO_NOTIF)
        lista_n = notifs_db.get("lista", [])

        # Marcar todas como leídas
        for n in lista_n: n["leida"] = True
        guardar_json(ARCHIVO_NOTIF, notifs_db)
        actualizar_badge_notif()

        controles = []
        if not lista_n:
            controles.append(
                ft.Container(alignment=ft.Alignment(0,0), padding=40,
                    content=ft.Column([
                        ft.Text("🔔", size=50),
                        ft.Text("No hay notificaciones", color=ft.Colors.GREY_500,
                            italic=True, size=15, text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10))
            )
        else:
            ICONOS = {
                "intercambio": (ft.Icons.SWAP_HORIZ, ft.Colors.BLUE_600, ft.Colors.BLUE_50),
                "evento":      (ft.Icons.EVENT,       ft.Colors.GREEN_600, ft.Colors.GREEN_50),
                "reputacion":  (ft.Icons.STAR,        ft.Colors.AMBER_600, ft.Colors.AMBER_50),
                "grupo":       (ft.Icons.GROUP,       ft.Colors.PURPLE_600, ft.Colors.PURPLE_50),
                "info":        (ft.Icons.INFO,        ft.Colors.GREY_600, ft.Colors.GREY_50),
            }
            for n in lista_n:
                tipo = n.get("tipo","info")
                icono, color, bg = ICONOS.get(tipo, ICONOS["info"])
                controles.append(
                    ft.Container(
                        padding=ft.Padding(14,12,14,12),
                        border_radius=12,
                        bgcolor=bg,
                        border=ft.Border.all(1, color),
                        shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.BLACK12, offset=ft.Offset(0,2)),
                        content=ft.Row([
                            ft.Container(
                                width=40, height=40, border_radius=20,
                                bgcolor=color,
                                alignment=ft.Alignment(0,0),
                                content=ft.Icon(icono, color=ft.Colors.WHITE, size=20),
                            ),
                            ft.Column([
                                ft.Text(n.get("msg",""), size=13, color=ft.Colors.BLUE_GREY_800,
                                    weight=ft.FontWeight.W_500),
                                ft.Text(n.get("fecha",""), size=11, color=ft.Colors.GREY_500),
                            ], spacing=2, expand=True),
                        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    )
                )

        def limpiar(e):
            guardar_json(ARCHIVO_NOTIF, {"lista":[]})
            actualizar_badge_notif()
            cambiar("notificaciones")

        return ft.Container(padding=ft.Padding(20,16,20,24), content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.NOTIFICATIONS, color=ft.Colors.BLUE_600, size=24),
                ft.Text("Notificaciones", size=20, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_GREY_900),
                ft.Container(expand=True),
                ft.TextButton("Limpiar todo", on_click=limpiar,
                    style=ft.ButtonStyle(color=ft.Colors.RED_400)),
            ], spacing=8),
            ft.Divider(height=6, color=ft.Colors.GREY_200),
            ft.Column(controles, spacing=8, scroll=ft.ScrollMode.AUTO),
        ], spacing=10, scroll=ft.ScrollMode.AUTO))

    # ── VISTA MERCADO ─────────────────────────────────────────────────
    def vista_mercado():
        from datetime import datetime
        mercado = cargar_mercado()
        lista_mercado = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
        msg_mercado   = ft.Text("", size=13, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)

        # Filtros
        filtro_sel = ["todos"]
        filtro_tipo_sel = ["todos"]

        TIPOS_ESPECIALES = {
            "ICONOS":   ("Íconos ⭐",    ft.Colors.AMBER_600),
            "MUSEO":    ("Museum 🏆",    ft.Colors.PURPLE_600),
            "PARALLELS":("Parallels 🎨", ft.Colors.BLUE_600),
            "COCACOLA": ("Especial 🥤", ft.Colors.RED_600),
            "CRUMPLE":  ("Crumple ✨",   ft.Colors.GREEN_600),
        }

        # Campos para publicar
        campo_estampa   = ft.Dropdown(
            label="Estampa especial",
            options=[ft.dropdown.Option(key=e["id"], text=f"{e['jugador']} — {e['tipo']}")
                     for cat in ESPECIALES.values() for e in cat["estampas"]],
            width=320, border_radius=10, bgcolor=ft.Colors.WHITE,
        )
        campo_precio    = ft.TextField(label="Precio ($MXN)", width=140,
            border_radius=10, bgcolor=ft.Colors.WHITE,
            keyboard_type=ft.KeyboardType.NUMBER)
        campo_acepta    = ft.TextField(label="También acepto intercambio por...", width=320,
            border_radius=10, bgcolor=ft.Colors.WHITE)
        campo_contacto  = ft.TextField(label="WhatsApp o contacto", width=220,
            border_radius=10, bgcolor=ft.Colors.WHITE)
        switch_intercambio = ft.Switch(label="Acepto intercambio", value=True,
            active_color=ft.Colors.GREEN_500)

        def cargar_lista(filtro="todos", tipo="todos"):
            lista_mercado.controls.clear()
            items = list(mercado.values())
            items.sort(key=lambda x: x.get("fecha",""), reverse=True)

            # Filtrar
            if filtro == "mis":
                items = [i for i in items if i.get("vendedor") == nombre_u[0]]
            if tipo != "todos":
                items = [i for i in items if i.get("categoria") == tipo]

            if not items:
                lista_mercado.controls.append(
                    ft.Container(alignment=ft.Alignment(0,0), padding=40,
                        content=ft.Column([
                            ft.Text("🛒", size=50),
                            ft.Text("No hay estampas en venta", color=ft.Colors.GREY_500,
                                italic=True, size=14, text_align=ft.TextAlign.CENTER),
                            ft.Text("¡Sé el primero en publicar!",
                                color=ft.Colors.GREY_400, size=12, text_align=ft.TextAlign.CENTER),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8))
                )
            else:
                for item in items:
                    es_mio = item.get("vendedor") == nombre_u[0]
                    cat    = item.get("categoria","ICONOS")
                    col    = COLORES_ESPECIALES.get(ESPECIALES.get(cat,{}).get("color","amber"), COLORES_ESPECIALES["amber"])
                    tipo_color = col["header"]

                    def make_contactar(contacto=item.get("contacto",""), jugador=item.get("jugador","")):
                        def contactar(e):
                            agregar_notificacion(f"📞 Contactaste al vendedor de {jugador}", "mercado")
                            try: actualizar_badge_notif()
                            except: pass
                            import subprocess
                            wa = contacto.replace(" ","").replace("-","").replace("+","")
                            if wa.isdigit():
                                subprocess.Popen(["cmd","/c","start",f"https://wa.me/52{wa}"])
                            snk(f"📱 Abriendo WhatsApp con {contacto}...")
                        return contactar

                    def make_eliminar(item_id=item.get("id","")):
                        def eliminar(e):
                            m = cargar_mercado()
                            if item_id in m:
                                del m[item_id]
                                guardar_mercado(m)
                                mercado.clear()
                                mercado.update(m)
                                cargar_lista(filtro_sel[0], filtro_tipo_sel[0])
                                try: lista_mercado.update(); page.update()
                                except: pass
                                snk("✅ Publicación eliminada")
                        return eliminar

                    lista_mercado.controls.append(
                        ft.Card(elevation=4, content=ft.Container(
                            padding=16, border_radius=16, bgcolor=ft.Colors.WHITE,
                            border=ft.Border.all(2, ft.Colors.AMBER_300 if not es_mio else ft.Colors.BLUE_300),
                            content=ft.Column([
                                # Header
                                ft.Row([
                                    ft.Container(
                                        padding=ft.Padding(10,8,10,8), border_radius=10,
                                        bgcolor=tipo_color,
                                        content=ft.Text("⭐", size=20),
                                    ),
                                    ft.Column([
                                        ft.Text(item.get("jugador","?"), size=16,
                                            weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                                        ft.Text(item.get("tipo",""), size=12, color=ft.Colors.GREY_600),
                                        ft.Text(item.get("pais",""), size=11, color=ft.Colors.GREY_500),
                                    ], spacing=2, expand=True),
                                    ft.Column([
                                        ft.Text(
                                            f"${item.get('precio','?')} MXN" if item.get("precio") else "Intercambio",
                                            size=18, weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.GREEN_700 if item.get("precio") else ft.Colors.BLUE_600,
                                        ),
                                        ft.Container(
                                            padding=ft.Padding(6,3,6,3), border_radius=20,
                                            bgcolor=ft.Colors.GREEN_100 if item.get("precio") else ft.Colors.BLUE_100,
                                            content=ft.Text(
                                                "💰 Venta" if item.get("precio") else "🔄 Intercambio",
                                                size=11,
                                                color=ft.Colors.GREEN_800 if item.get("precio") else ft.Colors.BLUE_800,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ),
                                    ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=4),
                                ], spacing=12),

                                ft.Divider(height=8, color=ft.Colors.GREY_100),

                                # Vendedor info
                                ft.Row([
                                    ft.Icon(ft.Icons.PERSON, color=ft.Colors.GREY_500, size=14),
                                    ft.Text(item.get("vendedor","?"), size=12, color=ft.Colors.GREY_600),
                                    ft.Container(expand=True),
                                    ft.Icon(ft.Icons.ACCESS_TIME, color=ft.Colors.GREY_400, size=12),
                                    ft.Text(item.get("fecha",""), size=11, color=ft.Colors.GREY_400),
                                ], spacing=4),

                                # Acepta intercambio
                                ft.Container(
                                    bgcolor=ft.Colors.BLUE_50, border_radius=8,
                                    padding=ft.Padding(8,6,8,6),
                                    content=ft.Text(
                                        f"🔄 También acepta: {item.get('acepta','No especificado')}",
                                        size=12, color=ft.Colors.BLUE_700,
                                    ),
                                    visible=bool(item.get("acepta") and item.get("intercambio")),
                                ),

                                ft.Divider(height=6, color=ft.Colors.GREY_100),

                                # Botones
                                ft.Row([
                                    ft.Button(
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.CHAT, color=ft.Colors.WHITE, size=16),
                                            ft.Text("Contactar", color=ft.Colors.WHITE,
                                                weight=ft.FontWeight.BOLD, size=13),
                                        ], tight=True, spacing=6),
                                        on_click=make_contactar(item.get("contacto",""), item.get("jugador","")),
                                        style=ft.ButtonStyle(
                                            bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE,
                                            padding=ft.Padding(16,10,16,10),
                                            shape=ft.RoundedRectangleBorder(radius=10)),
                                        visible=not es_mio,
                                    ) if not es_mio else ft.Container(),
                                    ft.Container(expand=True),
                                    ft.Container(
                                        padding=ft.Padding(8,4,8,4), border_radius=20,
                                        bgcolor=ft.Colors.BLUE_100,
                                        content=ft.Text("✏️ Mi publicación", size=11,
                                            color=ft.Colors.BLUE_700, weight=ft.FontWeight.BOLD),
                                        visible=es_mio,
                                    ),
                                    ft.IconButton(
                                        ft.Icons.DELETE_OUTLINE,
                                        icon_color=ft.Colors.RED_400, icon_size=20,
                                        on_click=make_eliminar(item.get("id","")),
                                        visible=es_mio,
                                        tooltip="Eliminar publicación",
                                    ) if es_mio else ft.Container(),
                                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            ], spacing=8)
                        ))
                    )
            try: lista_mercado.update()
            except: pass

        def publicar(e):
            if not campo_estampa.value:
                msg_mercado.value = "⚠️ Selecciona una estampa"
                msg_mercado.color = ft.Colors.ORANGE_700
                try: msg_mercado.update()
                except: pass
                return
            if not campo_precio.value and not switch_intercambio.value:
                msg_mercado.value = "⚠️ Agrega precio o activa intercambio"
                msg_mercado.color = ft.Colors.ORANGE_700
                try: msg_mercado.update()
                except: pass
                return

            # Encontrar info de la estampa
            est_info = None
            cat_key  = None
            for ck, cat in ESPECIALES.items():
                for est in cat["estampas"]:
                    if est["id"] == campo_estampa.value:
                        est_info = est; cat_key = ck; break
                if est_info: break

            if not est_info:
                msg_mercado.value = "❌ Estampa no encontrada"
                msg_mercado.color = ft.Colors.RED_700
                try: msg_mercado.update()
                except: pass
                return

            import uuid as _uuid
            item_id = str(_uuid.uuid4())[:8]
            m = cargar_mercado()
            m[item_id] = {
                "id":         item_id,
                "jugador":    est_info["jugador"],
                "tipo":       est_info["tipo"],
                "pais":       est_info["pais"],
                "categoria":  cat_key,
                "estampa_id": campo_estampa.value,
                "precio":     campo_precio.value.strip() if campo_precio.value else "",
                "intercambio": switch_intercambio.value,
                "acepta":     campo_acepta.value.strip(),
                "contacto":   campo_contacto.value.strip() or nombre_u[0],
                "vendedor":   nombre_u[0],
                "fecha":      datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            guardar_mercado(m)
            mercado.clear(); mercado.update(m)

            agregar_notificacion(
                f"🛒 Publicaste en venta: {est_info['jugador']} ({est_info['tipo']})",
                "mercado"
            )
            try: actualizar_badge_notif()
            except: pass

            msg_mercado.value = f"✅ ¡{est_info['jugador']} publicado en el mercado!"
            msg_mercado.color = ft.Colors.GREEN_700
            campo_precio.value = ""; campo_acepta.value = ""; campo_contacto.value = ""
            cargar_lista(filtro_sel[0], filtro_tipo_sel[0])
            try:
                msg_mercado.update(); campo_precio.update()
                campo_acepta.update(); campo_contacto.update()
                lista_mercado.update(); page.update()
            except: pass

        # Chips de filtro por tipo
        def chip_filtro(key, label, color):
            def click(e, k=key):
                filtro_tipo_sel[0] = k
                cargar_lista(filtro_sel[0], k)
                try: lista_mercado.update(); page.update()
                except: pass
            return ft.GestureDetector(on_tap=click, content=ft.Container(
                padding=ft.Padding(10,6,10,6), border_radius=20,
                bgcolor=color,
                content=ft.Text(label, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ))

        chips_filtro = ft.Row([
            chip_filtro("todos", "Todos 📋", ft.Colors.BLUE_GREY_600),
            chip_filtro("ICONOS", "Íconos ⭐", ft.Colors.AMBER_600),
            chip_filtro("MUSEO", "Museum 🏆", ft.Colors.PURPLE_600),
            chip_filtro("PARALLELS", "Parallels 🎨", ft.Colors.BLUE_600),
            chip_filtro("COCACOLA", "Especial 🥤", ft.Colors.RED_600),
            chip_filtro("CRUMPLE", "Crumple ✨", ft.Colors.GREEN_600),
        ], spacing=6, scroll=ft.ScrollMode.AUTO)

        def ver_mis(e):
            filtro_sel[0] = "mis"
            cargar_lista("mis", filtro_tipo_sel[0])
            try: lista_mercado.update(); page.update()
            except: pass

        def ver_todos(e):
            filtro_sel[0] = "todos"
            cargar_lista("todos", filtro_tipo_sel[0])
            try: lista_mercado.update(); page.update()
            except: pass

        cargar_lista()

        total_mercado = len(mercado)
        mis_publicaciones = sum(1 for i in mercado.values() if i.get("vendedor") == nombre_u[0])

        return ft.Container(padding=ft.Padding(20,16,20,24), content=ft.Column([
            # Stats rápidas
            ft.Row([
                ft.Container(expand=True, padding=14, border_radius=14, bgcolor=ft.Colors.WHITE,
                    border=ft.Border.all(1,ft.Colors.AMBER_200),
                    shadow=ft.BoxShadow(blur_radius=6,color=ft.Colors.BLACK12,offset=ft.Offset(0,2)),
                    content=ft.Column([ft.Icon(ft.Icons.STOREFRONT,color=ft.Colors.AMBER_600,size=22),
                        ft.Text(str(total_mercado),size=24,weight=ft.FontWeight.BOLD,color=ft.Colors.AMBER_700),
                        ft.Text("En venta",size=11,color=ft.Colors.GREY_500,text_align=ft.TextAlign.CENTER)],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=3)),
                ft.Container(expand=True, padding=14, border_radius=14, bgcolor=ft.Colors.WHITE,
                    border=ft.Border.all(1,ft.Colors.BLUE_200),
                    shadow=ft.BoxShadow(blur_radius=6,color=ft.Colors.BLACK12,offset=ft.Offset(0,2)),
                    content=ft.Column([ft.Icon(ft.Icons.SELL,color=ft.Colors.BLUE_600,size=22),
                        ft.Text(str(mis_publicaciones),size=24,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_600),
                        ft.Text("Mis publicaciones",size=11,color=ft.Colors.GREY_500,text_align=ft.TextAlign.CENTER)],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=3)),
            ], spacing=10),

            # Publicar
            ft.Container(padding=20, bgcolor=ft.Colors.WHITE, border_radius=18,
                shadow=ft.BoxShadow(blur_radius=12,color=ft.Colors.BLACK12,offset=ft.Offset(0,3)),
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.ADD_CIRCLE,color=ft.Colors.AMBER_600,size=22),
                        ft.Text("Publicar Estampa Especial",size=17,weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_GREY_800)],spacing=8),
                    ft.Text("Vende o intercambia tus estampas especiales repetidas",
                        size=12,color=ft.Colors.GREY_500),
                    ft.Divider(height=6,color=ft.Colors.GREY_100),
                    campo_estampa,
                    ft.Row([campo_precio, switch_intercambio], spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    campo_acepta,
                    campo_contacto,
                    ft.Button(
                        content=ft.Row([ft.Icon(ft.Icons.SELL,color=ft.Colors.WHITE),
                            ft.Text("Publicar en el Mercado",color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD)],tight=True,spacing=8),
                        on_click=publicar,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.AMBER_700,color=ft.Colors.WHITE,
                            padding=ft.Padding(20,12,20,12),
                            shape=ft.RoundedRectangleBorder(radius=12),elevation=4),
                    ),
                    ft.Row([msg_mercado],alignment=ft.MainAxisAlignment.CENTER),
                ],spacing=10)),

            ft.Divider(height=8,color=ft.Colors.TRANSPARENT),

            # Lista mercado
            ft.Container(padding=20,bgcolor=ft.Colors.WHITE,border_radius=18,
                shadow=ft.BoxShadow(blur_radius=12,color=ft.Colors.BLACK12,offset=ft.Offset(0,3)),
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.STOREFRONT,color=ft.Colors.AMBER_600,size=22),
                        ft.Text("Mercado de Especiales",size=17,weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_GREY_800),
                        ft.Container(expand=True),
                        ft.TextButton("Todos",on_click=ver_todos,
                            style=ft.ButtonStyle(color=ft.Colors.BLUE_600)),
                        ft.TextButton("Mis publicaciones",on_click=ver_mis,
                            style=ft.ButtonStyle(color=ft.Colors.AMBER_700)),
                    ],spacing=8),
                    chips_filtro,
                    ft.Divider(height=6,color=ft.Colors.GREY_100),
                    lista_mercado,
                ],spacing=10)),
        ],spacing=10,scroll=ft.ScrollMode.AUTO))

    def cambiar(nueva):
        vista[0]=nueva
        # Sincronizar índice del NavigationBar
        _sec_to_idx = {"album":0,"stats":1,"qr":2,"grupos":3}
        if nueva in _sec_to_idx:
            nav_bar.selected_index = _sec_to_idx[nueva]
            try: nav_bar.update()
            except: pass
        if nueva=="album": vista_c.content=vista_album();upd_tablero(pais_sel[0])
        elif nueva=="stats": vista_c.content=vista_stats()
        elif nueva=="qr": vista_c.content=vista_qr()
        elif nueva=="grupos": vista_c.content=vista_grupos()
        elif nueva=="especiales": vista_c.content=vista_especiales()
        elif nueva=="reputacion": vista_c.content=vista_reputacion()
        elif nueva=="eventos": vista_c.content=vista_eventos()
        elif nueva=="notificaciones": vista_c.content=vista_notificaciones()
        elif nueva=="mercado": vista_c.content=vista_mercado()
        try: vista_c.update()
        except: pass
        page.update()

    def on_pais(e): pais_sel[0]=e.control.value;upd_tablero(pais_sel[0]);page.update()

    def buscar(e):
        resultados.controls.clear()
        resultados.controls.append(ft.Container(alignment=ft.Alignment(0,0),padding=20,
            content=ft.Text("🔍 Buscando intercambios...",color=ft.Colors.BLUE_600,size=14)))
        try: resultados.update()
        except: pass

        def _buscar():
            mr=set(); mo=set()
            for k,v in album.items():
                if v==REPETIDA: mr.add(k)
                elif v==TENGO: mo.add(k)
            pa=pais_sel[0]; enc=0
            resultados.controls.clear()

            # Buscar en servidor si está activo
            usar_servidor = servidor_activo()
            usuarios = []

            if usar_servidor:
                try:
                    # Registrar primero
                    registrar_usuario(album, nombre_u[0], mi_lat, mi_lon)
                    # Obtener usuarios cercanos
                    r = requests.post(f"{SERVIDOR}/usuarios_cercanos",
                        json={"lat":mi_lat,"lon":mi_lon,"radio_km":10.0},timeout=5)
                    data = r.json()
                    for u in data.get("usuarios",[]):
                        if u["id"] == MI_ID: continue
                        # Obtener detalle del usuario
                        db_local = {}
                        if os.path.exists("usuarios_db.json"):
                            db_local = json.load(open("usuarios_db.json","r",encoding="utf-8"))
                        if u["id"] in db_local:
                            ud = db_local[u["id"]]
                            usuarios.append({
                                "nombre": ud["nombre"],
                                "repetidas": ud.get("repetidas",[]),
                                "faltantes": ud.get("faltantes",[]),
                                "lat": ud["lat"], "lon": ud["lon"],
                                "is_business": False,
                            })
                except: pass

            # Siempre incluir usuarios hardcodeados como respaldo
            for u in USUARIOS_DB:
                usuarios.append(u)

            for u in usuarios:
                sr=set(u["repetidas"]); sf=set(u["faltantes"])
                md={c for c in sr if c.startswith(pa) and c not in mo and c not in mr}
                ld={c for c in mr if c.startswith(pa) and c in sf}
                dist=(((mi_lat-u["lat"])**2+(mi_lon-u["lon"])**2)**0.5)*111
                if dist>5.0 and not u.get("is_business",False): continue
                if md and ld:
                    s=u.get("is_business",False)
                    resultados.controls.append(ft.Card(elevation=3,content=ft.Container(
                        padding=16,border_radius=14,
                        bgcolor=ft.Colors.AMBER_50 if s else ft.Colors.WHITE,
                        border=ft.Border.all(1.5,ft.Colors.AMBER_300 if s else ft.Colors.BLUE_100),
                        content=ft.Column([
                            ft.Row([
                                ft.Container(content=ft.Icon(ft.Icons.STOREFRONT if s else ft.Icons.PERSON,color=ft.Colors.WHITE,size=18),
                                    bgcolor=ft.Colors.AMBER_600 if s else ft.Colors.BLUE_500,border_radius=20,padding=6),
                                ft.Column([
                                    ft.Text(u["nombre"]+(" ⭐" if s else ""),weight=ft.FontWeight.BOLD,size=14,color=ft.Colors.BLUE_GREY_900),
                                    ft.Row([ft.Icon(ft.Icons.LOCATION_ON,size=12,color=ft.Colors.GREY_500),
                                        ft.Text(f"A {round(dist,1)} km",size=12,color=ft.Colors.GREY_500)],spacing=2),
                                ],spacing=1),
                            ],spacing=10),
                            ft.Divider(height=8,color=ft.Colors.GREY_100),
                            ft.Container(bgcolor=ft.Colors.GREEN_50,border_radius=8,padding=ft.Padding(8,6,8,6),
                                content=ft.Text(f"🟢 Te da: {', '.join(sorted(md))}",size=13,color=ft.Colors.GREEN_800)),
                            ft.Container(bgcolor=ft.Colors.BLUE_50,border_radius=8,padding=ft.Padding(8,6,8,6),
                                content=ft.Text(f"🔵 Tú le das: {', '.join(sorted(ld))}",size=13,color=ft.Colors.BLUE_800)),
                        ],spacing=8))))
                    enc+=1

            if enc==0:
                resultados.controls.append(ft.Container(alignment=ft.Alignment(0,0),padding=30,
                    content=ft.Column([ft.Text("😔",size=40),
                        ft.Text("No hay intercambios disponibles",
                            color=ft.Colors.GREY_500,italic=True,text_align=ft.TextAlign.CENTER,size=14),
                        ft.Text("Prueba marcando estampas como Repetidas (doble clic)",
                            color=ft.Colors.GREY_400,size=12,text_align=ft.TextAlign.CENTER),
                    ],horizontal_alignment=ft.CrossAxisAlignment.CENTER,spacing=8)))
            try: resultados.update(); page.update()
            except: pass

        import threading
        threading.Thread(target=_buscar, daemon=True).start()

    # ── NAVEGACIÓN INFERIOR (móvil) ──────────────────────────────────
    # Las 9 secciones se agrupan en 5 tabs visibles; el resto en un menú "Más"
    TABS_PRINCIPALES = [
        ("album",        ft.Icons.GRID_VIEW,      "Álbum"),
        ("stats",        ft.Icons.BAR_CHART,       "Stats"),
        ("qr",           ft.Icons.QR_CODE_SCANNER, "QR"),
        ("grupos",       ft.Icons.GROUP_WORK,      "Grupos"),
        ("mas",          ft.Icons.MORE_HORIZ,      "Más"),
    ]
    MAS_OPCIONES = [
        ("especiales",    ft.Icons.STAR,          "Especiales"),
        ("reputacion",    ft.Icons.STAR_RATE,      "Reputación"),
        ("eventos",       ft.Icons.EVENT,          "Eventos"),
        ("notificaciones",ft.Icons.NOTIFICATIONS,  "Alertas"),
        ("mercado",       ft.Icons.STOREFRONT,     "Mercado"),
    ]

    badge_notif=ft.Text("",size=9,color=ft.Colors.WHITE,weight=ft.FontWeight.BOLD)
    badge_container=ft.Container(width=16,height=16,border_radius=8,bgcolor=ft.Colors.RED_500,
        alignment=ft.Alignment(0,0),content=badge_notif,visible=False)

    def actualizar_badge_notif():
        n=contar_no_leidas()
        badge_notif.value=str(n) if n<10 else "9+"
        badge_container.visible=(n>0)
        try: badge_notif.update();badge_container.update()
        except: pass

    # Monitor en segundo plano para notificaciones automáticas
    def monitor_notificaciones():
        import time
        ya_notificados = set()  # Evitar repetir notificaciones
        while True:
            time.sleep(60)  # Revisar cada 60 segundos
            try:
                if servidor_activo():
                    mis_fal = {f"{c}{i}" for c,_,_ in PAISES for i in range(1,21)
                               if album.get(f"{c}{i}") not in (TENGO, REPETIDA)}
                    r=requests.post(f"{SERVIDOR}/usuarios_cercanos",
                        json={"lat":mi_lat,"lon":mi_lon,"radio_km":5.0},timeout=3)
                    data=r.json()
                    db_local=cargar_json("usuarios_db.json")
                    for u in data.get("usuarios",[]):
                        if u["id"]==MI_ID: continue
                        if u["id"] in ya_notificados: continue  # Ya notificamos de este usuario
                        ud=db_local.get(u["id"],{})
                        sus_rep=set(ud.get("repetidas",[]))
                        match=sus_rep & mis_fal
                        if match:
                            nombres_match=", ".join(sorted(match)[:3])
                            sufijo="..." if len(match)>3 else ""
                            agregar_notificacion(
                                f"🔔 {u['nombre']} está cerca y tiene {len(match)} estampas que te faltan: {nombres_match}{sufijo}",
                                "info"
                            )
                            ya_notificados.add(u["id"])
                            try: actualizar_badge_notif()
                            except: pass
            except: pass

    _th.Thread(target=monitor_notificaciones, daemon=True).start()
    actualizar_badge_notif()

    def mostrar_menu_mas(e):
        """Abre bottom sheet con las secciones secundarias."""
        opciones_controls = []
        for seccion, icono, etiqueta in MAS_OPCIONES:
            def _nav(ev, s=seccion):
                bs_mas.open = False; page.update()
                cambiar(s)
            opciones_controls.append(
                ft.ListTile(
                    leading=ft.Icon(icono, color="#2563EB", size=24),
                    title=ft.Text(etiqueta, size=15, weight=ft.FontWeight.W_600),
                    on_click=_nav,
                    min_vertical_padding=14,
                )
            )
        bs_mas = ft.BottomSheet(
            content=ft.Container(
                padding=ft.Padding(0, 12, 0, 24),
                content=ft.Column(
                    [ft.Container(
                        width=40, height=4, border_radius=2,
                        bgcolor=ft.Colors.GREY_300,
                        margin=ft.Margin(0,0,0,8),
                    )] + opciones_controls,
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True,
                ),
            ),
            bgcolor=ft.Colors.WHITE,
        )
        page.overlay.append(bs_mas)
        bs_mas.open = True
        page.update()

    nav_tab_idx = [0]
    TAB_SECCIONES = ["album","stats","qr","grupos","mas"]

    def _build_nav():
        dest = []
        for sec, icon, label in TABS_PRINCIPALES:
            dest.append(ft.NavigationBarDestination(
                icon=icon,
                label=label,
            ))
        return dest

    def on_nav_change(e):
        idx = e.control.selected_index
        nav_tab_idx[0] = idx
        sec = TAB_SECCIONES[idx]
        if sec == "mas":
            mostrar_menu_mas(e)
            # Mantener el tab anterior activo visualmente
            nav_bar.selected_index = nav_tab_idx[0]
            try: nav_bar.update()
            except: pass
        else:
            nav_tab_idx[0] = idx
            cambiar(sec)

    nav_bar = ft.NavigationBar(
        destinations=_build_nav(),
        selected_index=0,
        bgcolor=ft.Colors.WHITE,
        indicator_color=ft.Colors.with_opacity(0.15, "#2563EB"),
        shadow_color=ft.Colors.with_opacity(0.15, "#000000"),
        elevation=12,
        on_change=on_nav_change,
    )

    # Botones legacy (usados internamente en cambiar() para resaltar estado activo)
    btn_al=ft.Button(visible=False)
    btn_st=ft.Button(visible=False)
    btn_qr=ft.Button(visible=False)
    btn_gr=ft.Button(visible=False)
    btn_esp=ft.Button(visible=False)
    btn_rep=ft.Button(visible=False)
    btn_ev=ft.Button(visible=False)
    btn_notif=ft.Button(visible=False)
    btn_mkt=ft.Button(visible=False)
    header=ft.Container(
        padding=ft.Padding(10,8,12,8),
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1,-1), end=ft.Alignment(1,1),
            colors=["#0D1B3E", "#1A3A6B", "#2563EB"],
        ),
        shadow=ft.BoxShadow(blur_radius=16, color=ft.Colors.with_opacity(0.4,"#000000"), offset=ft.Offset(0,3)),
        content=ft.Row([
            ft.Row([
                ft.Text("⚽", size=28),
                ft.Column([
                    ft.Text("STICKERS", size=18, weight=ft.FontWeight.BOLD, color="#FCD34D"),
                    ft.Text("INTERCAMBIO DE ESTAMPAS", size=8, color=ft.Colors.with_opacity(0.8,"#FFFFFF"),
                        weight=ft.FontWeight.BOLD),
                ], spacing=1),
            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(expand=True),
            ft.Container(
                padding=ft.Padding(6,4,6,4),
                border_radius=8,
                bgcolor=ft.Colors.with_opacity(0.2, "#FFFFFF"),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.3, "#F59E0B")),
                content=ft.Column([
                    txt_ih,
                    txt_ph,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            ),
        ], alignment=ft.MainAxisAlignment.START,
           vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
    )

    # Layout móvil: header arriba, contenido expandible, nav abajo
    page.add(ft.Column([
        header,
        ft.Container(content=vista_c, expand=True, padding=ft.Padding(0,0,0,0)),
        nav_bar,
    ], spacing=0, expand=True))
    cambiar("album")

import os as _os_main
ft.app(main, assets_dir=_os_main.path.join(_os_main.path.dirname(_os_main.path.abspath(__file__)), "assets"))