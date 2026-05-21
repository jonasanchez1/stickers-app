import os
os.environ["PYTHONHTTPSVERIFY"] = "0"

import flet as ft

# --- BASE DE DATOS SIMULADA ---
USUARIOS_DB = [
    {
        "nombre": "Pedro (Usuario Gratis)",
        "repetidas": ["MEX10", "MEX18", "ARG5", "BRA12", "CAN3", "GER14", "FRA7"],
        "faltantes":  ["MEX5", "ARG10", "BRA20", "USA1", "URU11", "ESP9", "ITA4"],
        "lat": 31.7333, "lon": -106.4833,
        "is_business": False,
    },
    {
        "nombre": "Starbucks Misiones",
        "repetidas": ["MEX5", "ARG10", "BRA20", "USA1", "URU11", "ESP9", "ITA4"],
        "faltantes":  ["MEX10", "MEX18", "ARG5", "CAN3", "GER14", "FRA7"],
        "lat": 31.7400, "lon": -106.4900,
        "is_business": True,
    },
]

PAISES = [
    ("GER","Alemania 🇩🇪"), ("ANG","Angola 🇦🇴"), ("KSA","Arabia Saudita 🇸🇦"),
    ("ARG","Argentina 🇦🇷"), ("AUS","Australia 🇦🇺"), ("AUT","Austria 🇦🇹"),
    ("BEL","Bélgica 🇧🇪"), ("BRA","Brasil 🇧🇷"), ("CMR","Camerún 🇨🇲"),
    ("CAN","Canadá 🇨🇦"), ("CHI","Chile 🇨🇱"), ("COL","Colombia 🇨🇴"),
    ("KOR","Corea del Sur 🇰🇷"), ("CRC","Costa Rica 🇨🇷"), ("CRO","Croacia 🇭🇷"),
    ("DEN","Dinamarca 🇩🇰"), ("ECU","Ecuador 🇪🇨"), ("EGY","Egipto 🇪🇬"),
    ("SCO","Escocia 🏴󠁧󠁢󠁳󠁣󠁴󠁿"), ("ESP","España 🇪🇸"), ("USA","Estados Unidos 🇺🇸"),
    ("FRA","Francia 🇫🇷"), ("WAL","Gales 🏴󠁧󠁢󠁷󠁬󠁳󠁿"), ("GHA","Ghana 🇬🇭"),
    ("NED","Países Bajos 🇳🇱"), ("ENG","Inglaterra 🏴󠁧󠁢󠁥󠁮󠁧󠁿"), ("IRN","Irán 🇮🇷"),
    ("IRQ","Irak 🇮🇶"), ("ITA","Italia 🇮🇹"), ("JAM","Jamaica 🇯🇲"),
    ("JPN","Japón 🇯🇵"), ("MAR","Marruecos 🇲🇦"), ("MEX","México 🇲🇽"),
    ("NGA","Nigeria 🇳🇬"), ("NZL","Nueva Zelanda 🇳🇿"), ("PAN","Panamá 🇵🇦"),
    ("PER","Perú 🇵🇪"), ("POR","Portugal 🇵🇹"), ("COD","Rep. Dem. del Congo 🇨🇩"),
    ("SEN","Senegal 🇸🇳"), ("SRB","Serbia 🇷🇸"), ("SWE","Suecia 🇸🇪"),
    ("SUI","Suiza 🇨🇭"), ("TUN","Túnez 🇹🇳"), ("UKR","Ucrania 🇺🇦"),
    ("URU","Uruguay 🇺🇾"), ("UZB","Uzbekistán 🇺🇿"), ("VEN","Venezuela 🇻🇪"),
]

FALTA    = "falta"
TENGO    = "tengo"
REPETIDA = "repetida"

C_FALTA    = ft.Colors.BLUE_GREY_50
C_TENGO    = ft.Colors.GREEN_500
C_REPETIDA = ft.Colors.BLUE_500
T_OSCURO   = ft.Colors.BLUE_GREY_700
T_CLARO    = ft.Colors.WHITE

def obtener_estilo_estado(estado):
    if estado == TENGO:
        return C_TENGO, T_CLARO
    elif estado == REPETIDA:
        return C_REPETIDA, T_CLARO
    else:
        return C_FALTA, T_OSCURO


def main(page: ft.Page):
    page.title = "Panini Match Juárez"
    page.scroll = "adaptive"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_100
    page.padding = 24

    mi_album = {}
    pais_sel = ["MEX"]
    mi_lat, mi_lon = 31.7350, -106.4850

    resultados = ft.ListView(spacing=12, padding=10, height=280)

    grid_view_fijo = ft.GridView(
        runs_count=5,
        max_extent=65,
        child_aspect_ratio=1.0,
        spacing=10,
        expand=False,
    )
    grid_container = ft.Container(content=grid_view_fijo)

    def actualizar_tablero_visual(prefix):
        grid_container.content.controls.clear()
        celdas_locales = {}

        def on_tap(e, num):
            clave = f"{prefix}{num}"
            prev  = mi_album.get(clave, FALTA)
            nuevo = TENGO if prev == FALTA else FALTA
            mi_album[clave] = nuevo
            bg, fg = obtener_estilo_estado(nuevo)
            celdas_locales[num].bgcolor = bg
            celdas_locales[num].content.color = fg
            celdas_locales[num].border = (
                None if nuevo != FALTA
                else ft.Border.all(1, ft.Colors.BLUE_GREY_100)
            )
            celdas_locales[num].update()

        def on_doble_tap(e, num):
            clave = f"{prefix}{num}"
            mi_album[clave] = REPETIDA
            bg, fg = obtener_estilo_estado(REPETIDA)
            celdas_locales[num].bgcolor = bg
            celdas_locales[num].content.color = fg
            celdas_locales[num].border = None
            celdas_locales[num].update()

        for i in range(1, 21):
            estado_actual = mi_album.get(f"{prefix}{i}", FALTA)
            bg, fg = obtener_estilo_estado(estado_actual)
            cont = ft.Container(
                content=ft.Text(str(i), color=fg, weight=ft.FontWeight.BOLD, size=16),
                bgcolor=bg,
                border_radius=10,
                width=60,
                height=60,
                alignment=ft.alignment.center,
                border=ft.Border.all(1, ft.Colors.BLUE_GREY_100) if estado_actual == FALTA else None,
            )
            celdas_locales[i] = cont
            grid_container.content.controls.append(
                ft.GestureDetector(
                    content=cont,
                    on_tap=lambda e, n=i: on_tap(e, n),
                    on_double_tap=lambda e, n=i: on_doble_tap(e, n),
                )
            )

    def buscar(e):
        resultados.controls.clear()
        mis_repetidas = set()
        mis_obtenidas = set()
        for cromo, estado in mi_album.items():
            if estado == REPETIDA:
                mis_repetidas.add(cromo)
            elif estado == TENGO:
                mis_obtenidas.add(cromo)

        encontrados = 0
        prefix_actual = pais_sel[0]

        for u in USUARIOS_DB:
            sus_repetidas = set(u["repetidas"])
            sus_faltantes  = set(u["faltantes"])

            me_da = {c for c in sus_repetidas
                     if c.startswith(prefix_actual)
                     and c not in mis_obtenidas
                     and c not in mis_repetidas}

            le_doy = {c for c in mis_repetidas
                      if c.startswith(prefix_actual) and c in sus_faltantes}

            dist = (((mi_lat - u["lat"])**2 + (mi_lon - u["lon"])**2)**0.5) * 111

            if dist > 2.0 and not u["is_business"]:
                continue

            if me_da and le_doy:
                s = u["is_business"]
                resultados.controls.append(
                    ft.Card(
                        elevation=2,
                        content=ft.Container(
                            padding=16,
                            border_radius=12,
                            bgcolor=ft.Colors.AMBER_50 if s else ft.Colors.WHITE,
                            border=ft.Border.all(1, ft.Colors.AMBER_200 if s else ft.Colors.GREY_200),
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.STOREFRONT if s else ft.Icons.PERSON,
                                            color=ft.Colors.AMBER_700 if s else ft.Colors.BLUE_GREY_500),
                                    ft.Text(
                                        u["nombre"] + (" [SOCIO PATROCINADO]" if s else ""),
                                        weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.BLUE_GREY_900,
                                    ),
                                ], alignment=ft.MainAxisAlignment.START),
                                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                                ft.Text(f"🟢 Te da: {', '.join(sorted(me_da))}", size=14, weight=ft.FontWeight.W_500),
                                ft.Text(f"🔵 Tú le das: {', '.join(sorted(le_doy))}", size=14, weight=ft.FontWeight.W_500),
                                ft.Row([
                                    ft.Icon(ft.Icons.LOCATION_ON, size=14, color=ft.Colors.GREY_500),
                                    ft.Text(f"A {round(dist, 1)} km de distancia", size=12, color=ft.Colors.GREY_600),
                                ], spacing=4),
                            ], spacing=6),
                        ),
                    )
                )
                encontrados += 1

        if encontrados == 0:
            resultados.controls.append(
                ft.Container(
                    alignment=ft.alignment.center,
                    padding=20,
                    content=ft.Text(
                        "No hay propuestas de intercambio disponibles para esta selección nacional.",
                        color=ft.Colors.GREY_500, italic=True, text_align=ft.TextAlign.CENTER,
                    ),
                )
            )
        resultados.update()

    # Flet 0.85: Dropdown usa on_select (no on_change)
    def on_cambio_pais(e):
        pais_sel[0] = e.control.value
        actualizar_tablero_visual(pais_sel[0])
        page.update()

    # Flet 0.85: usar ft.Button en lugar de ft.ElevatedButton
    boton_busqueda = ft.Button(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.SEARCH, color=ft.Colors.WHITE),
                ft.Text("Buscar Intercambio Automático", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ],
            tight=True,
            spacing=8,
        ),
        on_click=buscar,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )

    leyenda = ft.Row([
        ft.Row([
            ft.Container(width=16, height=16, bgcolor=C_FALTA, border_radius=4,
                         border=ft.Border.all(1, ft.Colors.GREY_400)),
            ft.Text("Falta", size=13, color=ft.Colors.BLUE_GREY_800),
        ]),
        ft.Row([
            ft.Container(width=16, height=16, bgcolor=C_TENGO, border_radius=4),
            ft.Text("Tengo (1 clic)", size=13, color=ft.Colors.BLUE_GREY_800),
        ]),
        ft.Row([
            ft.Container(width=16, height=16, bgcolor=C_REPETIDA, border_radius=4),
            ft.Text("Repetida (Doble clic)", size=13, color=ft.Colors.BLUE_GREY_800),
        ]),
    ], spacing=16, alignment=ft.MainAxisAlignment.START)

    # Flet 0.85: Dropdown usa on_select
    dropdown = ft.Dropdown(
        label="Selección Nacional (48 Participantes)",
        value="MEX",
        options=[ft.dropdown.Option(key=c, text=l) for c, l in PAISES],
        width=360,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        on_select=on_cambio_pais,
    )

    page.add(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SPORTS_SOCCER, size=32, color=ft.Colors.BLUE_600),
                ft.Text("Panini Match 🏟️", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Text("Gestiona tus estampas y encuentra coleccionistas en Juárez de forma automática.",
                    size=14, color=ft.Colors.BLUE_GREY_600),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

            ft.Card(
                elevation=3,
                content=ft.Container(
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=16,
                    content=ft.Column([
                        ft.Text("Mi Álbum Dinámico", size=18, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_GREY_800),
                        leyenda,
                        ft.Divider(height=15, color=ft.Colors.GREY_200),
                        dropdown,
                        ft.Container(content=grid_container, padding=ft.Padding(top=10, left=0, right=0, bottom=0)),
                    ], spacing=12),
                ),
            ),

            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            ft.Row([boton_busqueda], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

            ft.Text("Intercambios Sugeridos Cercanos", size=18, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_GREY_800),
            resultados,
        ], spacing=10)
    )

    actualizar_tablero_visual("MEX")
    page.update()


ft.app(main)
