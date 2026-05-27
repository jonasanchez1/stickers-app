import os, json, random, threading, uuid
os.environ["PYTHONHTTPSVERIFY"] = "0"

import flet as ft
import qrcode
import requests

ARCHIVO_GUARDADO = "album_guardado.json"
SERVIDOR = "https://stickers-app-production-555a.up.railway.app"

ID_FILE = "mi_id.txt"
if os.path.exists(ID_FILE):
    with open(ID_FILE) as f: MI_ID = f.read().strip()
else:
    MI_ID = str(uuid.uuid4())[:8]
    with open(ID_FILE, "w") as f: f.write(MI_ID)

USUARIOS_DB = [
    {"nombre": "Pedro", "repetidas": ["MEX10","MEX18","ARG5","BRA12","CAN3","GER14","FRA7"],
     "faltantes": ["MEX5","ARG10","BRA20","USA1","URU11","ESP9","ITA4"], "lat": 31.7333, "lon": -106.4833, "is_business": False},
    {"nombre": "Starbucks Misiones", "repetidas": ["MEX5","ARG10","BRA20","USA1","URU11","ESP9","ITA4"],
     "faltantes": ["MEX10","MEX18","ARG5","CAN3","GER14","FRA7"], "lat": 31.7400, "lon": -106.4900, "is_business": True},
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
TOTAL_PAISES = len(PAISES)
TOTAL_ESTAMPAS = TOTAL_PAISES * 20
PAISES_DICT = {c: (n, i) for c, n, i in PAISES}

FALTA = "falta"; TENGO = "tengo"; REPETIDA = "repetida"
C_FALTA = ft.Colors.BLUE_GREY_50; C_TENGO = ft.Colors.GREEN_500; C_REPETIDA = ft.Colors.BLUE_400
T_OSCURO = ft.Colors.BLUE_GREY_600; T_CLARO = ft.Colors.WHITE
COLORES_CONFETI = [ft.Colors.RED_400, ft.Colors.YELLOW_400, ft.Colors.GREEN_400,
                   ft.Colors.BLUE_400, ft.Colors.PURPLE_400, ft.Colors.ORANGE_400]

def estilo(e):
    if e == TENGO: return C_TENGO, T_CLARO
    if e == REPETIDA: return C_REPETIDA, T_CLARO
    return C_FALTA, T_OSCURO

def cargar():
    if os.path.exists(ARCHIVO_GUARDADO):
        try:
            with open(ARCHIVO_GUARDADO, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {}

def guardar(album):
    try:
        with open(ARCHIVO_GUARDADO, "w", encoding="utf-8") as f:
            json.dump(album, f, ensure_ascii=False, indent=2)
        return True
    except: return False

def stats(album):
    pc = tt = tr = 0; det = []
    for c, n, i in PAISES:
        t = sum(1 for x in range(1, 21) if album.get(f"{c}{x}") in (TENGO, REPETIDA))
        r = sum(1 for x in range(1, 21) if album.get(f"{c}{x}") == REPETIDA)
        comp = (t == 20)
        if comp: pc += 1
        tt += t; tr += r; det.append((c, n, i, t, r, comp))
    return pc, tt, tr, round(tt / TOTAL_ESTAMPAS * 100, 1), det

def intercambio_qr(mi_album, sus_reps):
    sus_rep = set(sus_reps)
    mis_rep = {k for k, v in mi_album.items() if v == REPETIDA}
    mis_fal = {f"{c}{i}" for c, _, _ in PAISES for i in range(1, 21)
               if mi_album.get(f"{c}{i}") not in (TENGO, REPETIDA)}
    return sorted(sus_rep & mis_fal), sorted(mis_rep)

def servidor_activo():
    try: return requests.get(f"{SERVIDOR}/ping", timeout=2).ok
    except: return False

def registrar_usuario(album, nombre, lat, lon):
    reps = [k for k, v in album.items() if v == REPETIDA]
    fals = [f"{c}{i}" for c, _, _ in PAISES for i in range(1, 21)
            if album.get(f"{c}{i}") not in (TENGO, REPETIDA)]
    try:
        r = requests.post(f"{SERVIDOR}/registrar", json={
            "usuario_id": MI_ID, "nombre": nombre,
            "repetidas": reps, "faltantes": fals, "lat": lat, "lon": lon
        }, timeout=5)
        return r.json()
    except Exception as e: return {"ok": False, "mensaje": str(e)}

def buscar_grupos_api(lat, lon, radio_km=5.0):
    try:
        r = requests.post(f"{SERVIDOR}/buscar_grupos", json={
            "usuario_id": MI_ID, "lat": lat, "lon": lon, "radio_km": radio_km, "max_grupo": 5
        }, timeout=10)
        return r.json()
    except Exception as e: return {"ok": False, "grupos": [], "mensaje": str(e)}


def main(page: ft.Page):
    page.title = "Stickers — Intercambio de Estampas"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_100
    page.padding = 0
    page.scroll = None

    album = cargar()
    pais_sel = ["MEX"]
    nombre_u = ["Mi Usuario"]
    mi_lat, mi_lon = 31.7350, -106.4850

    txt_t = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600)
    txt_f = ft.Text("20", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_600)
    txt_r = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    barra = ft.ProgressBar(value=0, bgcolor=ft.Colors.GREY_200, color=ft.Colors.GREEN_500, height=14, border_radius=7)
    txt_prog = ft.Text("0/20", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600)
    txt_ph = ft.Text("México", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    txt_ih = ft.Text("[MX]", size=13, color=ft.Colors.BLUE_200)

    snack = ft.SnackBar(content=ft.Text(""), bgcolor=ft.Colors.GREEN_700)
    page.overlay.append(snack)
    grid_c = ft.Container(expand=True)
    vista_c = ft.Container(expand=True)
    resultados = ft.ListView(spacing=12, padding=10, height=300)

    # Referencias a botones de navegación
    btns_nav = {}

    def snk(msg, color=ft.Colors.GREEN_700):
        snack.content = ft.Text(msg, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
        snack.bgcolor = color; snack.open = True
        try: snack.update()
        except: pass

    def upd_cnt(prefix):
        t = sum(1 for k, v in album.items() if k.startswith(prefix) and v in (TENGO, REPETIDA))
        r = sum(1 for k, v in album.items() if k.startswith(prefix) and v == REPETIDA)
        txt_t.value = str(t - r); txt_f.value = str(max(20 - t, 0)); txt_r.value = str(r)
        barra.value = t / 20; txt_prog.value = f"{t}/20"
        try: txt_t.update(); txt_f.update(); txt_r.update(); barra.update(); txt_prog.update()
        except: pass

    def cerrar(dlg):
        dlg.open = False; page.update()

    def celebrar(np):
        piezas = [ft.Container(
            width=random.randint(8, 16), height=random.randint(8, 16),
            bgcolor=random.choice(COLORES_CONFETI), border_radius=random.randint(0, 8),
            left=random.randint(10, 380), top=random.randint(10, 200),
            rotate=ft.Rotate(random.uniform(0, 3.14)), opacity=random.uniform(0.7, 1.0)
        ) for _ in range(30)]
        dlg = ft.AlertDialog(
            modal=True, bgcolor=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=24),
            content=ft.Container(width=400, content=ft.Column([
                ft.Stack([
                    ft.Stack(piezas, width=400, height=220),
                    ft.Container(width=400, height=220, alignment=ft.Alignment(0, 0),
                        content=ft.Column([
                            ft.Text("🏆", size=60),
                            ft.Text("¡País Completado!", size=22, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_GREY_900, text_align=ft.TextAlign.CENTER)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4))
                ]),
                ft.Container(padding=ft.Padding(20, 0, 20, 20), content=ft.Column([
                    ft.Text("¡Completaste las 20 estampas de", size=14, color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER),
                    ft.Text(np, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700,
                        text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6))
            ], spacing=0)),
            actions=[ft.Button(
                content=ft.Row([ft.Icon(ft.Icons.CELEBRATION, color=ft.Colors.WHITE),
                    ft.Text("¡Genial!", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)],
                    tight=True, spacing=6),
                on_click=lambda e: cerrar(dlg),
                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE,
                    padding=ft.Padding(24, 12, 24, 12), shape=ft.RoundedRectangleBorder(radius=12))
            )],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
        page.overlay.append(dlg); dlg.open = True; page.update()

    def construir_grid(prefix):
        celdas = {}; ctrl = []; celebrado = [False]

        def check():
            if celebrado[0]: return
            if sum(1 for i in range(1, 21) if album.get(f"{prefix}{i}") in (TENGO, REPETIDA)) == 20:
                celebrado[0] = True
                n, _ = PAISES_DICT.get(prefix, (prefix, ""))
                celebrar(n)

        def tap(e, num):
            k = f"{prefix}{num}"
            nuevo = TENGO if album.get(k, FALTA) == FALTA else FALTA
            album[k] = nuevo; guardar(album)
            bg, fg = estilo(nuevo); c = celdas[num]
            c.bgcolor = bg; c.content.color = fg
            c.border = None if nuevo != FALTA else ft.border.all(1, ft.Colors.BLUE_GREY_200)
            c.shadow = ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK26, offset=ft.Offset(0, 2)) if nuevo != FALTA else None
            c.update(); upd_cnt(prefix); check()

        def dtap(e, num):
            k = f"{prefix}{num}"; album[k] = REPETIDA; guardar(album)
            bg, fg = estilo(REPETIDA); c = celdas[num]
            c.bgcolor = bg; c.content.color = fg
            c.border = None
            c.shadow = ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK26, offset=ft.Offset(0, 2))
            c.update(); upd_cnt(prefix); check()

        for i in range(1, 21):
            ea = album.get(f"{prefix}{i}", FALTA); bg, fg = estilo(ea)
            cont = ft.Container(
                content=ft.Text(str(i), color=fg, weight=ft.FontWeight.BOLD, size=15),
                bgcolor=bg, border_radius=12, width=62, height=62, alignment=ft.Alignment(0, 0),
                border=ft.border.all(1, ft.Colors.BLUE_GREY_200) if ea == FALTA else None,
                shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK26, offset=ft.Offset(0, 2)) if ea != FALTA else None
            )
            celdas[i] = cont
            ctrl.append(ft.GestureDetector(content=cont,
                on_tap=lambda e, n=i: tap(e, n),
                on_double_tap=lambda e, n=i: dtap(e, n)))

        filas = []
        for f in range(0, 20, 5):
            filas.append(ft.Row(ctrl[f:f + 5], spacing=8, alignment=ft.MainAxisAlignment.START))
        return ft.Column(filas, spacing=8)

    def upd_tablero(prefix):
        n, iso = PAISES_DICT.get(prefix, (prefix, "??"))
        txt_ph.value = n; txt_ih.value = f"[{iso}]"
        try: txt_ph.update(); txt_ih.update()
        except: pass
        grid_c.content = construir_grid(prefix)
        try: grid_c.update()
        except: pass
        upd_cnt(prefix)

    # ── VISTAS ───────────────────────────────────────────────────────

    def vista_album():
        def tc2(label, widget, color, icono):
            return ft.Container(expand=True, padding=14, border_radius=14, bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.GREY_200),
                shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK12, offset=ft.Offset(0, 2)),
                content=ft.Column([ft.Icon(icono, color=color, size=22), widget,
                    ft.Text(label, size=11, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER)],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3))

        cnt = ft.Row([
            tc2("Tengo", txt_t, ft.Colors.GREEN_600, ft.Icons.CHECK_CIRCLE),
            tc2("Faltan", txt_f, ft.Colors.ORANGE_600, ft.Icons.HELP_OUTLINE),
            tc2("Repetidas", txt_r, ft.Colors.BLUE_400, ft.Icons.COPY_ALL)
        ], spacing=10)

        def chip(color, texto):
            return ft.Row([ft.Container(width=13, height=13, bgcolor=color, border_radius=4),
                ft.Text(texto, size=12, color=ft.Colors.BLUE_GREY_700)], spacing=5)

        leyenda = ft.Row([
            chip(C_FALTA, "Falta"),
            chip(C_TENGO, "Tengo (1 clic)"),
            chip(C_REPETIDA, "Repetida (2 clics)")
        ], spacing=14)

        dd = ft.Dropdown(
            label="Selección Nacional", value=pais_sel[0],
            options=[ft.dropdown.Option(key=c, text=f"[{iso}]  {n}") for c, n, iso in PAISES],
            width=220, border_radius=10, bgcolor=ft.Colors.WHITE, on_change=on_pais)

        def reset(e):
            p = pais_sel[0]; nm, _ = PAISES_DICT.get(p, (p, ""))
            for i in range(1, 21): album.pop(f"{p}{i}", None)
            guardar(album); upd_tablero(p); page.update()
            snk(f"🔄 {nm} reiniciado", ft.Colors.ORANGE_700)

        btn_reset = ft.Button(
            content=ft.Row([ft.Icon(ft.Icons.REFRESH, color=ft.Colors.WHITE),
                ft.Text("Reiniciar", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=12)],
                tight=True, spacing=4),
            on_click=reset,
            style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE_600, color=ft.Colors.WHITE,
                padding=ft.Padding(12, 10, 12, 10), shape=ft.RoundedRectangleBorder(radius=10)))

        btn_bus = ft.Button(
            content=ft.Row([ft.Icon(ft.Icons.SEARCH, color=ft.Colors.WHITE),
                ft.Text("Buscar", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=14)],
                tight=True, spacing=6),
            on_click=buscar,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE,
                padding=ft.Padding(20, 12, 20, 12), shape=ft.RoundedRectangleBorder(radius=12), elevation=4))

        btn_save = ft.Button(
            content=ft.Row([ft.Icon(ft.Icons.SAVE, color=ft.Colors.WHITE),
                ft.Text("Guardar", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=14)],
                tight=True, spacing=6),
            on_click=lambda e: snk("✅ Guardado") if guardar(album) else snk("❌ Error", ft.Colors.RED_700),
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE,
                padding=ft.Padding(20, 12, 20, 12), shape=ft.RoundedRectangleBorder(radius=12), elevation=4))

        return ft.Column([
            ft.Container(padding=ft.Padding(16, 12, 16, 0), content=cnt),
            ft.Container(padding=ft.Padding(16, 8, 16, 8),
                content=ft.Container(padding=20, bgcolor=ft.Colors.WHITE, border_radius=18,
                    shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK12, offset=ft.Offset(0, 3)),
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.GRID_VIEW, color=ft.Colors.BLUE_600, size=20),
                            ft.Text("Mi Álbum", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
                            ft.Container(expand=True),
                            ft.Row([ft.Icon(ft.Icons.CLOUD_DONE, color=ft.Colors.GREEN_400, size=16),
                                ft.Text("Auto-guardado", size=11, color=ft.Colors.GREEN_400)], spacing=4)], spacing=8),
                        leyenda,
                        ft.Divider(height=8, color=ft.Colors.GREY_100),
                        ft.Row([dd, ft.Container(expand=True), btn_reset], spacing=8),
                        ft.Column([
                            ft.Row([ft.Text("Progreso", size=12, color=ft.Colors.GREY_500), txt_prog],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            barra
                        ], spacing=5),
                        ft.Container(content=grid_c, padding=ft.Padding(0, 6, 0, 0)),
                    ], spacing=12))),
            ft.Container(padding=ft.Padding(16, 0, 16, 8),
                content=ft.Row([btn_bus, btn_save], alignment=ft.MainAxisAlignment.CENTER, spacing=12)),
            ft.Container(padding=ft.Padding(16, 0, 16, 4),
                content=ft.Row([ft.Icon(ft.Icons.SWAP_HORIZ, color=ft.Colors.BLUE_600, size=20),
                    ft.Text("Intercambios Sugeridos", size=17, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_800)], spacing=8)),
            ft.Container(padding=ft.Padding(16, 0, 16, 16), content=resultados),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    def vista_stats():
        pc, tt, tr, pct, det = stats(album)

        def tc(titulo, val, sub, color, icono):
            return ft.Container(expand=True, padding=16, border_radius=16, bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.GREY_200),
                shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK12, offset=ft.Offset(0, 2)),
                content=ft.Column([ft.Icon(icono, color=color, size=26),
                    ft.Text(str(val), size=28, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(titulo, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_700),
                    ft.Text(sub, size=11, color=ft.Colors.GREY_500)],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4))

        resumen = ft.Row([
            tc("Países\nCompletos", pc, f"de {TOTAL_PAISES}", ft.Colors.GREEN_600, ft.Icons.EMOJI_EVENTS),
            tc("Estampas", tt, f"de {TOTAL_ESTAMPAS}", ft.Colors.BLUE_600, ft.Icons.COLLECTIONS),
            tc("Completado", f"{pct}%", "del total", ft.Colors.PURPLE_600, ft.Icons.PIE_CHART),
            tc("Repetidas", tr, "para intercambio", ft.Colors.ORANGE_600, ft.Icons.COPY_ALL),
        ], spacing=8)

        det_ord = sorted(det, key=lambda x: (not x[5], -x[3]))
        filas = []
        for c, n, iso, t, r, comp in det_ord:
            cb = ft.Colors.GREEN_500 if comp else (ft.Colors.BLUE_400 if t > 0 else ft.Colors.GREY_300)
            filas.append(ft.Container(padding=ft.Padding(12, 8, 12, 8), border_radius=10,
                bgcolor=ft.Colors.GREEN_50 if comp else ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.GREEN_200 if comp else ft.Colors.GREY_100),
                content=ft.Row([
                    ft.Container(width=36, height=36, border_radius=18,
                        bgcolor=ft.Colors.GREEN_500 if comp else ft.Colors.GREY_200,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text("✓" if comp else str(t),
                            color=ft.Colors.WHITE if comp else ft.Colors.GREY_600,
                            size=13, weight=ft.FontWeight.BOLD)),
                    ft.Column([
                        ft.Row([ft.Text(f"[{iso}] {n}", size=13, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREEN_800 if comp else ft.Colors.BLUE_GREY_800),
                            ft.Container(expand=True),
                            ft.Text(f"{t}/20", size=12, color=ft.Colors.GREY_600)]),
                        ft.ProgressBar(value=t / 20, bgcolor=ft.Colors.GREY_100, color=cb, height=6, border_radius=3),
                    ], expand=True, spacing=4),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)))

        return ft.Column([
            ft.Container(padding=ft.Padding(16, 12, 16, 8), content=resumen),
            ft.Container(padding=ft.Padding(16, 0, 16, 8),
                content=ft.Container(padding=20, bgcolor=ft.Colors.WHITE, border_radius=18,
                    shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK12, offset=ft.Offset(0, 3)),
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.BAR_CHART, color=ft.Colors.PURPLE_600, size=22),
                            ft.Text("Progreso General", size=17, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_GREY_800)], spacing=8),
                        ft.Column([
                            ft.Row([ft.Text("Progreso general", size=13, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_GREY_700),
                                ft.Text(f"{pct}%", size=13, weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.GREEN_600)],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.ProgressBar(value=pct / 100, bgcolor=ft.Colors.GREY_200,
                                color=ft.Colors.GREEN_500, height=16, border_radius=8)
                        ], spacing=6),
                    ], spacing=12))),
            ft.Container(padding=ft.Padding(16, 0, 16, 16),
                content=ft.Container(padding=20, bgcolor=ft.Colors.WHITE, border_radius=18,
                    shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK12, offset=ft.Offset(0, 3)),
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.FLAG, color=ft.Colors.BLUE_600, size=22),
                            ft.Text("Progreso por País", size=17, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_GREY_800),
                            ft.Container(expand=True),
                            ft.Text(f"{pc} completos ✓", size=12, color=ft.Colors.GREEN_600,
                                weight=ft.FontWeight.BOLD)], spacing=8),
                        ft.Divider(height=6, color=ft.Colors.GREY_100),
                        ft.Column(filas, spacing=6),
                    ], spacing=10))),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    def vista_qr():
        txt_st = ft.Text("", size=13, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
        res_scan = ft.Column([], spacing=8)
        campo = ft.TextField(label="Tu nombre", value=nombre_u[0], width=260, border_radius=10, bgcolor=ft.Colors.WHITE)
        qr_texto_field = ft.TextField(value="", read_only=True, multiline=True, min_lines=3, max_lines=4,
            label="Tu código QR (cópialo y mándalo por WhatsApp)",
            border_radius=10, bgcolor=ft.Colors.GREY_50, visible=False, text_size=10)
        btn_copiar = ft.Button(
            content=ft.Row([ft.Icon(ft.Icons.COPY, color=ft.Colors.WHITE, size=16),
                ft.Text("Copiar código", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)],
                tight=True, spacing=6),
            visible=False,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE,
                padding=ft.Padding(16, 10, 16, 10), shape=ft.RoundedRectangleBorder(radius=10)))

        def gen(e):
            nombre_u[0] = campo.value or "Mi Usuario"
            try:
                reps = [k for k, v in album.items() if v == REPETIDA]
                fals = [f"{c}{i}" for c, _, _ in PAISES for i in range(1, 21)
                        if album.get(f"{c}{i}") not in (TENGO, REPETIDA)]
                texto_qr = f"STICKERS|{MI_ID}|{nombre_u[0]}|{','.join(reps)}|{','.join(fals[:50])}"
                qr_texto_field.value = texto_qr
                qr_texto_field.visible = True
                btn_copiar.visible = True
                def _copiar(ev):
                    page.set_clipboard(texto_qr)
                    txt_st.value = "✅ ¡Copiado! Pégalo en WhatsApp"
                    txt_st.color = ft.Colors.GREEN_700
                    try: txt_st.update()
                    except: pass
                btn_copiar.on_click = _copiar
                txt_st.value = "✅ QR generado — cópialo y mándalo"
                txt_st.color = ft.Colors.GREEN_700
            except Exception as ex:
                txt_st.value = f"❌ Error: {ex}"; txt_st.color = ft.Colors.RED_700
            try: txt_st.update(); qr_texto_field.update(); btn_copiar.update(); page.update()
            except: pass

        def pegar_qr(e):
            campo_pegar = ft.TextField(label="Pega aquí el código QR",
                multiline=True, min_lines=3, max_lines=5,
                border_radius=10, bgcolor=ft.Colors.WHITE, width=320)
            def leer(ev):
                txt = campo_pegar.value.strip()
                if txt:
                    dlg.open = False; page.update()
                    procesar_qr_texto(txt)
                else:
                    campo_pegar.error_text = "Pega el código primero"
                    try: campo_pegar.update()
                    except: pass
            dlg = ft.AlertDialog(modal=True, bgcolor=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=16),
                title=ft.Text("Pegar código QR", weight=ft.FontWeight.BOLD, size=16),
                content=ft.Container(width=340, content=ft.Column([
                    ft.Text("Pide a la otra persona su código y pégalo aquí.", size=13, color=ft.Colors.GREY_600),
                    campo_pegar], spacing=10)),
                actions=[
                    ft.Button(content=ft.Text("Cancelar", color=ft.Colors.GREY_700),
                        on_click=lambda e: cerrar(dlg),
                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_200,
                            padding=ft.Padding(16, 10, 16, 10), shape=ft.RoundedRectangleBorder(radius=10))),
                    ft.Button(content=ft.Text("Leer QR", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        on_click=leer,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE,
                            padding=ft.Padding(16, 10, 16, 10), shape=ft.RoundedRectangleBorder(radius=10)))],
                actions_alignment=ft.MainAxisAlignment.END)
            page.overlay.append(dlg); dlg.open = True; page.update()

        def procesar_qr_texto(leido):
            if leido.startswith("STICKERS|"):
                partes = leido.split("|")
                nom = partes[2] if len(partes) > 2 else "Otro"
                reps = partes[3].split(",") if len(partes) > 3 and partes[3] else []
            else:
                partes = leido.split("|", 1)
                nom = partes[0]
                reps = partes[1].split(",") if len(partes) > 1 and partes[1] else []
            me_da, le_doy = intercambio_qr(album, reps)
            txt_st.value = f"✅ QR de {nom} leído"; txt_st.color = ft.Colors.GREEN_700
            res_scan.controls.clear()
            res_scan.controls.append(
                ft.Container(padding=16, border_radius=14, bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1.5, ft.Colors.BLUE_200),
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK12, offset=ft.Offset(0, 2)),
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.SWAP_HORIZ, color=ft.Colors.BLUE_600, size=22),
                            ft.Text(f"Intercambio con {nom}", size=16, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_GREY_900)], spacing=8),
                        ft.Divider(height=8, color=ft.Colors.GREY_100),
                        ft.Container(bgcolor=ft.Colors.GREEN_50, border_radius=10, padding=12,
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.Icons.ARROW_DOWNWARD, color=ft.Colors.GREEN_700, size=16),
                                    ft.Text(f"Recibes ({len(me_da)})", size=13,
                                        weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)]),
                                ft.Text(", ".join(me_da) if me_da else "Ninguna", size=13, color=ft.Colors.GREEN_900)
                            ], spacing=4)),
                        ft.Container(bgcolor=ft.Colors.BLUE_50, border_radius=10, padding=12,
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.Icons.ARROW_UPWARD, color=ft.Colors.BLUE_700, size=16),
                                    ft.Text(f"Das ({len(le_doy)})", size=13,
                                        weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)]),
                                ft.Text(", ".join(le_doy) if le_doy else "Ninguna", size=13, color=ft.Colors.BLUE_900)
                            ], spacing=4)),
                    ], spacing=10)))
            try: txt_st.update(); res_scan.update(); page.update()
            except: pass

        btn_gen = ft.Button(
            content=ft.Row([ft.Icon(ft.Icons.QR_CODE_2, color=ft.Colors.WHITE),
                ft.Text("Generar mi QR", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)],
                tight=True, spacing=8),
            on_click=gen,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE,
                padding=ft.Padding(20, 12, 20, 12), shape=ft.RoundedRectangleBorder(radius=12), elevation=4))
        btn_pegar = ft.Button(
            content=ft.Row([ft.Icon(ft.Icons.CONTENT_PASTE, color=ft.Colors.WHITE),
                ft.Text("Pegar código QR", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)],
                tight=True, spacing=8),
            on_click=pegar_qr,
            style=ft.ButtonStyle(bgcolor=ft.Colors.PURPLE_600, color=ft.Colors.WHITE,
                padding=ft.Padding(20, 12, 20, 12), shape=ft.RoundedRectangleBorder(radius=12), elevation=4))

        return ft.Column([
            ft.Container(padding=ft.Padding(16, 12, 16, 8),
                content=ft.Container(padding=16, bgcolor=ft.Colors.WHITE, border_radius=18,
                    shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK12, offset=ft.Offset(0, 3)),
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.QR_CODE_2, color=ft.Colors.BLUE_600, size=22),
                            ft.Text("Mi Código QR", size=17, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_GREY_800)], spacing=8),
                        ft.Container(padding=10, border_radius=10, bgcolor=ft.Colors.BLUE_50,
                            border=ft.border.all(1, ft.Colors.BLUE_100),
                            content=ft.Column([
                                ft.Text("📋 Cómo intercambiar:", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                                ft.Text("1️⃣ Genera tu QR y cópialo", size=12, color=ft.Colors.BLUE_700),
                                ft.Text("2️⃣ Mándalo por WhatsApp", size=12, color=ft.Colors.BLUE_700),
                                ft.Text("3️⃣ Pega el código de la otra persona", size=12, color=ft.Colors.BLUE_700),
                            ], spacing=3)),
                        campo,
                        ft.Row([btn_gen], alignment=ft.MainAxisAlignment.CENTER),
                        qr_texto_field,
                        ft.Row([btn_copiar], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([txt_st], alignment=ft.MainAxisAlignment.CENTER),
                    ], spacing=12))),
            ft.Container(padding=ft.Padding(16, 0, 16, 16),
                content=ft.Container(padding=16, bgcolor=ft.Colors.WHITE, border_radius=18,
                    shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK12, offset=ft.Offset(0, 3)),
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.QR_CODE_SCANNER, color=ft.Colors.PURPLE_600, size=22),
                            ft.Text("Leer QR de otro", size=17, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_GREY_800)], spacing=8),
                        ft.Row([btn_pegar], alignment=ft.MainAxisAlignment.CENTER),
                        res_scan,
                    ], spacing=12))),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    def vista_grupos():
        txt_estado = ft.Text("", size=13, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
        txt_servidor = ft.Text("", size=12)
        lista_grupos = ft.Column([], spacing=12)
        campo_nombre = ft.TextField(label="Tu nombre", value=nombre_u[0], width=200, border_radius=10, bgcolor=ft.Colors.WHITE)
        campo_radio = ft.TextField(label="Radio (km)", value="5", width=90, border_radius=10, bgcolor=ft.Colors.WHITE)
        buscando = [False]

        def check_server():
            if servidor_activo():
                txt_servidor.value = "🟢 Servidor conectado"
                txt_servidor.color = ft.Colors.GREEN_700
            else:
                txt_servidor.value = "🔴 Servidor desconectado"
                txt_servidor.color = ft.Colors.RED_700
            try: txt_servidor.update()
            except: pass

        def registrar_y_buscar(e):
            if buscando[0]: return
            buscando[0] = True
            nombre_u[0] = campo_nombre.value or "Mi Usuario"
            try: radio = float(campo_radio.value)
            except: radio = 5.0
            txt_estado.value = "📡 Registrando álbum..."
            txt_estado.color = ft.Colors.BLUE_600
            lista_grupos.controls.clear()
            try: txt_estado.update(); lista_grupos.update()
            except: pass

            def _buscar():
                try:
                    res_reg = registrar_usuario(album, nombre_u[0], mi_lat, mi_lon)
                    if not res_reg.get("ok"):
                        txt_estado.value = f"❌ {res_reg.get('mensaje', 'Error al registrar')}"
                        txt_estado.color = ft.Colors.RED_700
                        try: txt_estado.update()
                        except: pass
                        buscando[0] = False
                        return
                    txt_estado.value = "🔍 Buscando grupos..."
                    txt_estado.color = ft.Colors.BLUE_600
                    try: txt_estado.update()
                    except: pass
                    res = buscar_grupos_api(mi_lat, mi_lon, radio)
                    grupos = res.get("grupos", [])
                    lista_grupos.controls.clear()
                    if not grupos:
                        lista_grupos.controls.append(
                            ft.Container(alignment=ft.Alignment(0, 0), padding=30,
                                content=ft.Column([
                                    ft.Text("😔", size=40),
                                    ft.Text("No se encontraron grupos cercanos",
                                        color=ft.Colors.GREY_500, italic=True,
                                        text_align=ft.TextAlign.CENTER, size=14),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)))
                        txt_estado.value = "✅ Búsqueda completa"
                    else:
                        txt_estado.value = f"✅ ¡{len(grupos)} grupos encontrados!"
                        txt_estado.color = ft.Colors.GREEN_700
                        for i, g in enumerate(grupos):
                            lista_grupos.controls.append(tarjeta_grupo(g, i + 1))
                    try: txt_estado.update(); lista_grupos.update(); page.update()
                    except: pass
                except Exception as ex:
                    txt_estado.value = f"❌ Error: {ex}"
                    txt_estado.color = ft.Colors.RED_700
                    try: txt_estado.update()
                    except: pass
                finally:
                    buscando[0] = False

            threading.Thread(target=_buscar, daemon=True).start()

        def tarjeta_grupo(g, num):
            miembros = g["miembros"]; tam = g["tamaño"]; total = g["total_estampas"]
            if tam >= 4: color_header = ft.Colors.PURPLE_600; emoji = "🎯"
            elif tam == 3: color_header = ft.Colors.BLUE_600; emoji = "🔄"
            else: color_header = ft.Colors.GREEN_600; emoji = "🤝"
            filas_m = []
            for m in miembros:
                es_yo = (m["id"] == MI_ID)
                recibe_de = m.get("recibe", [])
                estampas_recibe = [f"{est} (de {r['de']})" for r in recibe_de for est in r["estampas"]]
                filas_m.append(ft.Container(padding=ft.Padding(10, 8, 10, 8), border_radius=8,
                    bgcolor=ft.Colors.BLUE_50 if es_yo else ft.Colors.GREY_50,
                    border=ft.border.all(1, ft.Colors.BLUE_200 if es_yo else ft.Colors.GREY_200),
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.PERSON,
                            color=ft.Colors.BLUE_600 if es_yo else ft.Colors.GREY_600, size=16),
                            ft.Text(m["nombre"] + (" (Tú)" if es_yo else ""), size=13,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_800 if es_yo else ft.Colors.BLUE_GREY_800),
                            ft.Container(expand=True),
                            ft.Text(f"📍 {m['dist_km']} km", size=11, color=ft.Colors.GREY_500)], spacing=6),
                        ft.Text(f"Recibe: {', '.join(estampas_recibe)}" if estampas_recibe else "No recibe en este grupo",
                            size=12, color=ft.Colors.GREEN_700 if estampas_recibe else ft.Colors.GREY_400)
                    ], spacing=4)))
            return ft.Card(elevation=4, content=ft.Container(padding=16, border_radius=16,
                bgcolor=ft.Colors.WHITE, border=ft.border.all(1.5, color_header),
                content=ft.Column([
                    ft.Container(padding=ft.Padding(12, 10, 12, 10), border_radius=10, bgcolor=color_header,
                        content=ft.Row([ft.Text(emoji, size=20),
                            ft.Column([ft.Text(f"Grupo #{num} — {tam} personas", size=15,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text(f"{total} estampas intercambiables", size=12,
                                    color=ft.Colors.WHITE70)], spacing=2, expand=True)], spacing=10)),
                    ft.Divider(height=10, color=ft.Colors.GREY_100),
                    ft.Text("Participantes:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_700),
                    ft.Column(filas_m, spacing=6),
                ], spacing=10)))

        threading.Thread(target=check_server, daemon=True).start()

        btn_buscar = ft.Button(
            content=ft.Row([ft.Icon(ft.Icons.GROUP_WORK, color=ft.Colors.WHITE),
                ft.Text("Buscar Grupos", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=15)],
                tight=True, spacing=8),
            on_click=registrar_y_buscar,
            style=ft.ButtonStyle(bgcolor=ft.Colors.PURPLE_600, color=ft.Colors.WHITE,
                padding=ft.Padding(24, 14, 24, 14), shape=ft.RoundedRectangleBorder(radius=12), elevation=4))

        return ft.Column([
            ft.Container(padding=ft.Padding(16, 12, 16, 16),
                content=ft.Container(padding=20, bgcolor=ft.Colors.WHITE, border_radius=18,
                    shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK12, offset=ft.Offset(0, 3)),
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.GROUP_WORK, color=ft.Colors.PURPLE_600, size=22),
                            ft.Text("Intercambio Grupal", size=17, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_GREY_800)], spacing=8),
                        txt_servidor,
                        ft.Text("Busca grupos de 2-5 personas cercanas para intercambiar.",
                            size=12, color=ft.Colors.GREY_500),
                        ft.Divider(height=8, color=ft.Colors.GREY_100),
                        ft.Row([campo_nombre, campo_radio], spacing=10),
                        ft.Row([btn_buscar], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([txt_estado], alignment=ft.MainAxisAlignment.CENTER),
                    ], spacing=12))),
            ft.Container(padding=ft.Padding(16, 0, 16, 16), content=lista_grupos),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    # ── NAVEGACIÓN Y CAMBIO DE VISTA ─────────────────────────────────

    def cambiar(nueva):
        # Actualizar colores botones nav
        for key, btn in btns_nav.items():
            if btn is not None:
                activo = (nueva == key)
                btn.style = ft.ButtonStyle(
                    bgcolor=ft.Colors.BLUE_600 if activo else ft.Colors.BLUE_GREY_700,
                    color=ft.Colors.WHITE,
                    padding=ft.Padding(12, 10, 12, 10),
                    shape=ft.RoundedRectangleBorder(radius=10))
                try: btn.update()
                except: pass

        # Cargar vista
        if nueva == "album":
            vista_c.content = vista_album()
            upd_tablero(pais_sel[0])
        elif nueva == "stats":
            vista_c.content = vista_stats()
        elif nueva == "qr":
            vista_c.content = vista_qr()
        elif nueva == "grupos":
            vista_c.content = vista_grupos()

        try: vista_c.update()
        except: pass
        page.update()

    def on_pais(e):
        pais_sel[0] = e.control.value
        upd_tablero(pais_sel[0])
        page.update()

    def buscar(e):
        resultados.controls.clear()
        resultados.controls.append(ft.Container(alignment=ft.Alignment(0, 0), padding=20,
            content=ft.Text("🔍 Buscando intercambios...", color=ft.Colors.BLUE_600, size=14)))
        try: resultados.update()
        except: pass

        def _buscar():
            mr = set(); mo = set()
            for k, v in album.items():
                if v == REPETIDA: mr.add(k)
                elif v == TENGO: mo.add(k)
            pa = pais_sel[0]; enc = 0
            resultados.controls.clear()
            usuarios = list(USUARIOS_DB)
            if servidor_activo():
                try:
                    registrar_usuario(album, nombre_u[0], mi_lat, mi_lon)
                    r = requests.post(f"{SERVIDOR}/usuarios_cercanos",
                        json={"lat": mi_lat, "lon": mi_lon, "radio_km": 10.0}, timeout=5)
                    data = r.json()
                    db_local = {}
                    if os.path.exists("usuarios_db.json"):
                        db_local = json.load(open("usuarios_db.json", "r", encoding="utf-8"))
                    for u in data.get("usuarios", []):
                        if u["id"] == MI_ID: continue
                        if u["id"] in db_local:
                            ud = db_local[u["id"]]
                            usuarios.append({"nombre": ud["nombre"], "repetidas": ud.get("repetidas", []),
                                "faltantes": ud.get("faltantes", []), "lat": ud["lat"], "lon": ud["lon"],
                                "is_business": False})
                except: pass
            for u in usuarios:
                sr = set(u["repetidas"]); sf = set(u["faltantes"])
                md = {c for c in sr if c.startswith(pa) and c not in mo and c not in mr}
                ld = {c for c in mr if c.startswith(pa) and c in sf}
                dist = (((mi_lat - u["lat"]) ** 2 + (mi_lon - u["lon"]) ** 2) ** 0.5) * 111
                if dist > 5.0 and not u.get("is_business", False): continue
                if md and ld:
                    s = u.get("is_business", False)
                    resultados.controls.append(ft.Card(elevation=3, content=ft.Container(
                        padding=16, border_radius=14,
                        bgcolor=ft.Colors.AMBER_50 if s else ft.Colors.WHITE,
                        border=ft.border.all(1.5, ft.Colors.AMBER_300 if s else ft.Colors.BLUE_100),
                        content=ft.Column([
                            ft.Row([ft.Container(
                                content=ft.Icon(ft.Icons.STOREFRONT if s else ft.Icons.PERSON,
                                    color=ft.Colors.WHITE, size=18),
                                bgcolor=ft.Colors.AMBER_600 if s else ft.Colors.BLUE_500,
                                border_radius=20, padding=6),
                                ft.Column([
                                    ft.Text(u["nombre"] + (" ⭐" if s else ""),
                                        weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLUE_GREY_900),
                                    ft.Row([ft.Icon(ft.Icons.LOCATION_ON, size=12, color=ft.Colors.GREY_500),
                                        ft.Text(f"A {round(dist, 1)} km", size=12, color=ft.Colors.GREY_500)],
                                        spacing=2)], spacing=1)], spacing=10),
                            ft.Divider(height=8, color=ft.Colors.GREY_100),
                            ft.Container(bgcolor=ft.Colors.GREEN_50, border_radius=8, padding=ft.Padding(8, 6, 8, 6),
                                content=ft.Text(f"🟢 Te da: {', '.join(sorted(md))}", size=13, color=ft.Colors.GREEN_800)),
                            ft.Container(bgcolor=ft.Colors.BLUE_50, border_radius=8, padding=ft.Padding(8, 6, 8, 6),
                                content=ft.Text(f"🔵 Tú le das: {', '.join(sorted(ld))}", size=13, color=ft.Colors.BLUE_800)),
                        ], spacing=8))))
                    enc += 1
            if enc == 0:
                resultados.controls.append(ft.Container(alignment=ft.Alignment(0, 0), padding=30,
                    content=ft.Column([ft.Text("😔", size=40),
                        ft.Text("No hay intercambios disponibles", color=ft.Colors.GREY_500,
                            italic=True, text_align=ft.TextAlign.CENTER, size=14),
                        ft.Text("Marca estampas como Repetidas (doble clic)",
                            color=ft.Colors.GREY_400, size=12, text_align=ft.TextAlign.CENTER)],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)))
            try: resultados.update(); page.update()
            except: pass

        threading.Thread(target=_buscar, daemon=True).start()

    # ── BOTONES DE NAVEGACIÓN ────────────────────────────────────────
    btn_al = ft.Button(
        content=ft.Row([ft.Icon(ft.Icons.GRID_VIEW, color=ft.Colors.WHITE, size=14),
            ft.Text("Álbum", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=12)],
            tight=True, spacing=4),
        on_click=lambda e: cambiar("album"),
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE,
            padding=ft.Padding(12, 10, 12, 10), shape=ft.RoundedRectangleBorder(radius=10)))

    btn_st = ft.Button(
        content=ft.Row([ft.Icon(ft.Icons.BAR_CHART, color=ft.Colors.WHITE, size=14),
            ft.Text("Stats", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=12)],
            tight=True, spacing=4),
        on_click=lambda e: cambiar("stats"),
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_GREY_700, color=ft.Colors.WHITE,
            padding=ft.Padding(12, 10, 12, 10), shape=ft.RoundedRectangleBorder(radius=10)))

    btn_qr = ft.Button(
        content=ft.Row([ft.Icon(ft.Icons.QR_CODE_SCANNER, color=ft.Colors.WHITE, size=14),
            ft.Text("QR", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=12)],
            tight=True, spacing=4),
        on_click=lambda e: cambiar("qr"),
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_GREY_700, color=ft.Colors.WHITE,
            padding=ft.Padding(12, 10, 12, 10), shape=ft.RoundedRectangleBorder(radius=10)))

    btn_gr = ft.Button(
        content=ft.Row([ft.Icon(ft.Icons.GROUP_WORK, color=ft.Colors.WHITE, size=14),
            ft.Text("Grupos", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=12)],
            tight=True, spacing=4),
        on_click=lambda e: cambiar("grupos"),
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_GREY_700, color=ft.Colors.WHITE,
            padding=ft.Padding(12, 10, 12, 10), shape=ft.RoundedRectangleBorder(radius=10)))

    btns_nav["album"] = btn_al
    btns_nav["stats"] = btn_st
    btns_nav["qr"] = btn_qr
    btns_nav["grupos"] = btn_gr

    # ── HEADER Y LAYOUT PRINCIPAL ────────────────────────────────────
    header = ft.Container(
        padding=ft.Padding(20, 16, 20, 16),
        gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
            colors=["#0D1B3E", "#1A3A6B", "#2563EB"]),
        content=ft.Row([
            ft.Column([
                ft.Row([ft.Icon(ft.Icons.SPORTS_SOCCER, size=26, color=ft.Colors.WHITE),
                    ft.Text("Stickers App", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)],
                    spacing=8),
                ft.Text("Intercambia estampas en Juárez", size=11, color=ft.Colors.BLUE_100)
            ], spacing=3, expand=True),
            ft.Column([txt_ih, txt_ph], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

    nav = ft.Container(
        bgcolor=ft.Colors.BLUE_GREY_900, padding=ft.Padding(12, 8, 12, 8),
        content=ft.Row([btn_al, btn_st, btn_qr, btn_gr], spacing=8))

    page.add(ft.Column([header, nav, vista_c], spacing=0, expand=True))
    cambiar("album")


ft.app(target=main)