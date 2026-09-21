"""
Lista de compras · maqueta visual con Kivy + KivyMD
====================================================

Reproduce las cuatro pantallas del diseño:
  1. Inicio          (saludo + botón "Nueva lista")
  2. Listas          ("Mis listas" + tarjeta "Compra semanal")
  3. Detalle         (progreso + artículos con checkbox)
  4. Ajustes         (tema oscuro, notificaciones, idioma)

Por ahora es una maqueta: la navegación, el marcado de artículos y el
interruptor de tema funcionan a nivel visual, pero no se guarda nada.

Instalación (dentro del entorno virtual, en Windows):
    pip install kivy kivymd
Ejecución:
    python main.py

Opcional: si copias Inter-Regular.ttf e Inter-Bold.ttf en una carpeta
"fonts" junto a este archivo, la app usará la tipografía Inter (la del
diseño). Si no existen, usa Roboto, que ya viene con Kivy.
"""

import os

from kivy.config import Config
from kivy.utils import platform

# En escritorio, la ventana simula el tamaño de un teléfono. Debe definirse
# ANTES de importar la ventana de Kivy (kivy.core.window).
if platform in ("win", "linux", "macosx"):
    Config.set("graphics", "width", "392")
    Config.set("graphics", "height", "800")

from kivy.animation import Animation
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.lang.builder import global_idmap
from kivy.metrics import dp, sp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.widget import Widget
from kivy.utils import escape_markup, get_color_from_hex

from kivymd.app import MDApp

# ─────────────────────────────────────────────────────────────────────────
#  Paleta de colores (tomada del diseño)
# ─────────────────────────────────────────────────────────────────────────
PALETTE = {
    "BG": "#0A0B0F",  # fondo de pantalla
    "SURFACE": "#14161B",  # tarjetas y filas
    "SURFACE_ALT": "#1C1F26",  # botón atrás, ícono de la tarjeta, píldora activa
    "NAV_BG": "#0E1015",  # barra de navegación inferior
    "BORDER": "#23262E",  # borde de tarjetas
    "ACCENT": "#BEF24B",  # verde lima
    "ON_ACCENT": "#0A0B0F",  # texto/íconos sobre el verde lima
    "TEXT": "#FFFFFF",  # texto principal
    "MUTED": "#9599A4",  # texto secundario
    "SUBTLE": "#6E7280",  # íconos y etiquetas inactivas de la barra
    "TRACK": "#2A2D35",  # riel de la barra de progreso / interruptor apagado
    "CHECK_BORDER": "#7F8390",  # borde del checkbox vacío
}
COLORS = {name: get_color_from_hex(value) for name, value in PALETTE.items()}


def mix(color_a, color_b, t):
    """Interpola entre dos colores RGBA (t = 0 → a, t = 1 → b)."""
    return [a + (b - a) * t for a, b in zip(color_a, color_b)]


# Nombres disponibles dentro del código KV (colores, dp/sp y mix).
global_idmap.update(COLORS)
global_idmap.update({"dp": dp, "sp": sp, "mix": mix})


# ─────────────────────────────────────────────────────────────────────────
#  Datos de ejemplo
# ─────────────────────────────────────────────────────────────────────────
LIST_DATE = "Lunes, 14 de septiembre"
SAMPLE_ITEMS = [
    # (nombre, cantidad, completado)
    ("Leche", "1 litro", True),
    ("Pan integral", "1 paquete", True),
    ("Tomates", "6 unidades", False),
    ("Café", "250 g", False),
    ("Huevos", "12 unidades", False),
    ("Aceite de oliva", "1 botella", False),
]


# ─────────────────────────────────────────────────────────────────────────
#  Tipografía
# ─────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def register_fonts():
    """Usa Inter si está en ./fonts; de lo contrario, Roboto (incluida)."""
    regular = os.path.join(BASE_DIR, "fonts", "Inter-Regular.ttf")
    bold = os.path.join(BASE_DIR, "fonts", "Inter-Bold.ttf")
    if os.path.exists(regular) and os.path.exists(bold):
        LabelBase.register(name="Inter", fn_regular=regular, fn_bold=bold)
        return "Inter"
    return "Roboto"


# ─────────────────────────────────────────────────────────────────────────
#  Widgets reutilizables (el estilo está en el bloque KV de más abajo)
# ─────────────────────────────────────────────────────────────────────────
class Pressable(ButtonBehavior):
    """Mezcla que da retroalimentación visual al presionar."""


class BaseTxt(Label):
    """Etiqueta base con la tipografía y el color por defecto."""


class Txt(BaseTxt):
    """Texto que ocupa todo el ancho disponible y ajusta su altura."""


class TxtAuto(BaseTxt):
    """Texto que se ajusta exactamente a su contenido (ancho y alto)."""


class Card(BoxLayout):
    """Contenedor con esquinas redondeadas, relleno y borde."""

    fill_color = ColorProperty([0, 0, 0, 0])
    border_color = ColorProperty([0, 0, 0, 0])
    radius = NumericProperty(dp(20))


class TapCard(Pressable, Card):
    """Tarjeta que se puede tocar."""


class PillButton(Pressable, AnchorLayout):
    """Botón verde lima en forma de píldora, con ícono y texto."""

    text = StringProperty()
    icon = StringProperty("plus")


class IconButton(Pressable, AnchorLayout):
    """Botón cuadrado redondeado con un ícono (p. ej. el botón atrás)."""

    icon = StringProperty("arrow-left")


class NavItem(Pressable, AnchorLayout):
    """Elemento de la barra inferior; el activo se resalta con una píldora."""

    key = StringProperty()
    icon = StringProperty()
    text = StringProperty()
    active = BooleanProperty(False)


class SettingRow(TapCard):
    """Fila de la pantalla de ajustes (ícono + texto + control a la derecha)."""

    icon = StringProperty()
    text = StringProperty()


class CheckMark(Widget):
    """Casilla redondeada; vacía o rellena en verde lima con una palomita."""

    active = BooleanProperty(False)


class SoftProgress(Widget):
    """Barra de progreso delgada con extremos redondeados (valor 0 a 1)."""

    value = NumericProperty(0)


class ToggleSwitch(Pressable, Widget):
    """Interruptor con pista verde lima y perilla oscura."""

    active = BooleanProperty(True)
    progress = NumericProperty(1)  # 0 = apagado, 1 = encendido (animado)

    def on_release(self):
        self.active = not self.active
        Animation(progress=1 if self.active else 0, duration=0.15).start(self)


class ShoppingItem(Pressable, Card):
    """Fila de un artículo: casilla, nombre y cantidad."""

    title = StringProperty()
    quantity = StringProperty()
    done = BooleanProperty(False)
    title_markup = StringProperty()

    def on_title(self, *_):
        self._sync_title()

    def on_done(self, *_):
        self._sync_title()
        app = MDApp.get_running_app()
        if app is not None:
            app.refresh_progress()

    def on_release(self):
        self.done = not self.done

    def _sync_title(self):
        text = escape_markup(self.title)
        self.title_markup = f"[s]{text}[/s]" if self.done else text


# ─────────────────────────────────────────────────────────────────────────
#  Interfaz (lenguaje KV)
# ─────────────────────────────────────────────────────────────────────────
KV = r"""
# ══════════ Base ══════════════════════════════════════════════════════════

<Pressable>:
    opacity: 0.8 if self.state == "down" else 1

<BaseTxt>:
    font_name: app.font_name
    color: TEXT
    font_size: sp(16)
    halign: "left"
    valign: "middle"

<Txt>:
    size_hint_y: None
    text_size: self.width, None
    height: self.texture_size[1]

<TxtAuto>:
    size_hint: None, None
    text_size: None, None
    size: self.texture_size

<Icon@MDIcon>:
    theme_font_size: "Custom"
    font_size: sp(24)
    icon_color: TEXT

# ══════════ Componentes ═══════════════════════════════════════════════════

<Card>:
    canvas.before:
        Color:
            rgba: self.fill_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.radius]
        Color:
            rgba: self.border_color
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, self.radius)
            width: 1

<PillButton>:
    anchor_x: "center"
    anchor_y: "center"
    size_hint: None, None
    height: dp(54)
    width: content.width + dp(40)
    canvas.before:
        Color:
            rgba: ACCENT
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2]
    BoxLayout:
        id: content
        size_hint: None, None
        height: dp(54)
        width: self.minimum_width
        spacing: dp(8)
        Icon:
            icon: root.icon
            icon_color: ON_ACCENT
            font_size: sp(20)
            pos_hint: {"center_y": .5}
        TxtAuto:
            text: root.text
            bold: True
            color: ON_ACCENT
            font_size: sp(17)
            pos_hint: {"center_y": .5}

<IconButton>:
    anchor_x: "center"
    anchor_y: "center"
    size_hint: None, None
    size: dp(44), dp(44)
    canvas.before:
        Color:
            rgba: SURFACE
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
    Icon:
        icon: root.icon
        icon_color: TEXT
        font_size: sp(22)

<NavItem>:
    anchor_x: "center"
    anchor_y: "center"
    canvas.before:
        Color:
            rgba: SURFACE_ALT if self.active else (0, 0, 0, 0)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(18)]
    BoxLayout:
        orientation: "vertical"
        size_hint: 1, None
        height: self.minimum_height
        spacing: dp(4)
        Icon:
            icon: root.icon
            icon_color: ACCENT if root.active else SUBTLE
            font_size: sp(24)
            pos_hint: {"center_x": .5}
        TxtAuto:
            text: root.text
            bold: root.active
            color: TEXT if root.active else SUBTLE
            font_size: sp(12.5)
            pos_hint: {"center_x": .5}

<CheckMark>:
    size_hint: None, None
    size: dp(26), dp(26)
    canvas:
        # Casilla vacía: anillo gris (borde) + centro del color de la fila
        Color:
            rgba: ACCENT if self.active else CHECK_BORDER
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]
        Color:
            rgba: (0, 0, 0, 0) if self.active else SURFACE
        RoundedRectangle:
            pos: self.x + dp(2.2), self.y + dp(2.2)
            size: self.width - dp(4.4), self.height - dp(4.4)
            radius: [dp(5.8)]
        # Palomita (solo cuando está marcada)
        Color:
            rgba: ON_ACCENT if self.active else (0, 0, 0, 0)
        Line:
            points:
                [ \
                self.x + self.width * .28, self.y + self.height * .50, \
                self.x + self.width * .44, self.y + self.height * .33, \
                self.x + self.width * .73, self.y + self.height * .68 \
                ]
            width: dp(1.8)
            cap: "round"
            joint: "round"

<SoftProgress>:
    size_hint_y: None
    height: dp(5)
    canvas:
        Color:
            rgba: TRACK
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2]
        Color:
            rgba: ACCENT
        RoundedRectangle:
            pos: self.pos
            size: max(self.width * self.value, self.height if self.value > 0 else 0), self.height
            radius: [self.height / 2]

<ToggleSwitch>:
    size_hint: None, None
    size: dp(50), dp(30)
    canvas:
        Color:
            rgba: mix(TRACK, ACCENT, self.progress)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2]
        Color:
            rgba: BG
        Ellipse:
            pos:
                self.x + dp(4) + (self.width - dp(8) - dp(22)) * self.progress, \
                self.y + dp(4)
            size: dp(22), dp(22)

<ShoppingItem>:
    size_hint_y: None
    height: dp(62)
    padding: dp(18), 0
    spacing: dp(14)
    radius: dp(16)
    fill_color: SURFACE
    CheckMark:
        active: root.done
        pos_hint: {"center_y": .5}
    BoxLayout:
        orientation: "vertical"
        size_hint_y: None
        height: self.minimum_height
        pos_hint: {"center_y": .5}
        spacing: dp(1)
        Txt:
            text: root.title_markup
            markup: True
            font_size: sp(16.5)
            color: MUTED if root.done else TEXT
        Txt:
            text: root.quantity
            font_size: sp(13)
            color: MUTED

<SettingRow>:
    size_hint_y: None
    height: dp(62)
    padding: dp(18), 0, dp(16), 0
    spacing: dp(14)
    radius: dp(16)
    fill_color: SURFACE
    Icon:
        icon: root.icon
        icon_color: MUTED
        font_size: sp(22)
        pos_hint: {"center_y": .5}
    Txt:
        text: root.text
        font_size: sp(16.5)
        pos_hint: {"center_y": .5}

<BottomNav@BoxLayout>:
    size_hint_y: None
    height: dp(84)
    padding: dp(14), dp(11)
    spacing: dp(6)
    canvas.before:
        Color:
            rgba: NAV_BG
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: BORDER
        Line:
            points: self.x, self.top, self.right, self.top
            width: 1
    NavItem:
        key: "inicio"
        icon: "home-outline"
        text: "Inicio"
        active: app.current_tab == self.key
        on_release: app.go(self.key)
    NavItem:
        key: "listas"
        icon: "format-list-checks"
        text: "Listas"
        active: app.current_tab == self.key
        on_release: app.go(self.key)
    NavItem:
        key: "ajustes"
        icon: "tune-variant"
        text: "Ajustes"
        active: app.current_tab == self.key
        on_release: app.go(self.key)

# ══════════ Pantallas ═════════════════════════════════════════════════════

<InicioScreen@MDScreen>:
    name: "inicio"
    BoxLayout:
        orientation: "vertical"
        padding: dp(24), dp(64), dp(24), dp(40)
        spacing: dp(14)
        Txt:
            text: "Hola, ¿qué\nnecesitas\ncomprar?"
            font_size: sp(38)
            bold: True
            line_height: 1.08
        Txt:
            text: "Crea una lista y mantén todo lo importante\nen un solo lugar."
            font_size: sp(16)
            color: MUTED
            line_height: 1.25
        Widget:
        AnchorLayout:
            anchor_x: "right"
            anchor_y: "bottom"
            size_hint_y: None
            height: dp(54)
            PillButton:
                text: "Nueva lista"
                icon: "plus"
                on_release: app.new_list()

<ListasScreen@MDScreen>:
    name: "listas"
    BoxLayout:
        orientation: "vertical"
        padding: dp(24), dp(64), dp(24), dp(24)
        spacing: dp(26)
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            spacing: dp(12)
            BoxLayout:
                orientation: "vertical"
                spacing: dp(2)
                Txt:
                    text: "Mis listas"
                    font_size: sp(30)
                    bold: True
                Txt:
                    text: "{} {}".format(app.lists_count, "lista activa" if app.lists_count == 1 else "listas activas")
                    font_size: sp(14.5)
                    color: MUTED
            PillButton:
                text: "Agregar"
                icon: "plus"
                pos_hint: {"top": 1}
                on_release: app.new_list()
        TapCard:
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height
            padding: dp(24), dp(24), dp(24), dp(22)
            spacing: dp(20)
            fill_color: SURFACE
            border_color: BORDER
            radius: dp(22)
            on_release: app.go("detalle")
            BoxLayout:
                size_hint_y: None
                height: dp(48)
                spacing: dp(16)
                AnchorLayout:
                    size_hint: None, None
                    size: dp(48), dp(48)
                    canvas.before:
                        Color:
                            rgba: SURFACE_ALT
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(14)]
                    Icon:
                        icon: "basket-outline"
                        icon_color: ACCENT
                        font_size: sp(26)
                BoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    pos_hint: {"center_y": .5}
                    spacing: dp(2)
                    Txt:
                        text: "Compra semanal"
                        bold: True
                        font_size: sp(17)
                    Txt:
                        text: "{} artículos · {} completados".format(app.total_items, app.done_items)
                        font_size: sp(14)
                        color: MUTED
                Icon:
                    icon: "chevron-right"
                    icon_color: MUTED
                    font_size: sp(20)
                    pos_hint: {"center_y": .5}
            BoxLayout:
                size_hint_y: None
                height: dp(18)
                spacing: dp(9)
                Widget:
                    size_hint: None, None
                    size: dp(8), dp(8)
                    pos_hint: {"center_y": .5}
                    canvas:
                        Color:
                            rgba: ACCENT
                        Ellipse:
                            pos: self.pos
                            size: self.size
                Txt:
                    text: "Actualizada hoy"
                    font_size: sp(12.5)
                    color: MUTED
                    pos_hint: {"center_y": .5}
        Widget:

<DetalleScreen@MDScreen>:
    name: "detalle"
    BoxLayout:
        orientation: "vertical"
        padding: dp(24), dp(56), dp(24), dp(16)
        spacing: dp(22)
        BoxLayout:
            size_hint_y: None
            height: dp(52)
            spacing: dp(16)
            IconButton:
                icon: "arrow-left"
                pos_hint: {"center_y": .5}
                on_release: app.go("listas")
            BoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                pos_hint: {"center_y": .5}
                spacing: dp(1)
                Txt:
                    text: "Compra semanal"
                    font_size: sp(28)
                    bold: True
                Txt:
                    text: app.list_date
                    font_size: sp(14)
                    color: MUTED
            Icon:
                icon: "dots-horizontal"
                icon_color: MUTED
                font_size: sp(24)
                pos_hint: {"center_y": .5}
        BoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(9)
            BoxLayout:
                size_hint_y: None
                height: dp(16)
                Txt:
                    text: "{} de {} completados".format(app.done_items, app.total_items)
                    font_size: sp(13)
                    color: MUTED
                TxtAuto:
                    text: "{}%".format(app.percent)
                    font_size: sp(13)
                    bold: True
                    color: ACCENT
            SoftProgress:
                value: app.progress
        ScrollView:
            bar_width: 0
            do_scroll_x: False
            BoxLayout:
                id: item_list
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)

<AjustesScreen@MDScreen>:
    name: "ajustes"
    BoxLayout:
        orientation: "vertical"
        padding: dp(24), dp(64), dp(24), dp(24)
        spacing: dp(34)
        BoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: dp(56)
            spacing: dp(2)
            Txt:
                text: "Ajustes"
                font_size: sp(30)
                bold: True
            Txt:
                text: "Personaliza tu experiencia de compra."
                font_size: sp(14.5)
                color: MUTED
        BoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(8)
            SettingRow:
                icon: "moon-waning-crescent"
                text: "Tema oscuro"
                ToggleSwitch:
                    active: True
                    pos_hint: {"center_y": .5}
            SettingRow:
                icon: "bell-outline"
                text: "Notificaciones"
                Icon:
                    icon: "chevron-right"
                    icon_color: MUTED
                    font_size: sp(20)
                    pos_hint: {"center_y": .5}
            SettingRow:
                icon: "web"
                text: "Idioma"
                TxtAuto:
                    text: "Español"
                    color: MUTED
                    font_size: sp(15)
                    pos_hint: {"center_y": .5}
                Icon:
                    icon: "chevron-right"
                    icon_color: MUTED
                    font_size: sp(20)
                    pos_hint: {"center_y": .5}
        Widget:

# ══════════ Raíz ══════════════════════════════════════════════════════════

MDBoxLayout:
    orientation: "vertical"
    canvas.before:
        Color:
            rgba: BG
        Rectangle:
            pos: self.pos
            size: self.size
    MDScreenManager:
        id: sm
        InicioScreen:
        ListasScreen:
        DetalleScreen:
        AjustesScreen:
    BottomNav:
"""


# ─────────────────────────────────────────────────────────────────────────
#  Aplicación
# ─────────────────────────────────────────────────────────────────────────
class ShoppingListApp(MDApp):
    font_name = StringProperty("Roboto")
    current_tab = StringProperty("inicio")  # pestaña resaltada en la barra
    list_date = StringProperty(LIST_DATE)

    lists_count = NumericProperty(1)
    total_items = NumericProperty(0)
    done_items = NumericProperty(0)
    progress = NumericProperty(0)  # 0..1
    percent = NumericProperty(0)  # 0..100

    SCREEN_ORDER = ("inicio", "listas", "detalle", "ajustes")

    def build(self):
        self.title = "Lista de compras"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Lime"
        self.font_name = register_fonts()
        Window.clearcolor = COLORS["BG"]
        return Builder.load_string(KV)

    def on_start(self):
        sm = self.root.ids.sm
        sm.transition = SlideTransition(duration=0.2)

        items_box = sm.get_screen("detalle").ids.item_list
        for title, quantity, done in SAMPLE_ITEMS:
            items_box.add_widget(ShoppingItem(title=title, quantity=quantity, done=done))
        self.refresh_progress()

    # ── Navegación ──────────────────────────────────────────────────────
    def go(self, screen_name):
        sm = self.root.ids.sm
        if sm.current == screen_name:
            return
        order = self.SCREEN_ORDER
        forward = order.index(screen_name) > order.index(sm.current)
        sm.transition.direction = "left" if forward else "right"
        sm.current = screen_name
        # El detalle de una lista pertenece a la pestaña "Listas".
        self.current_tab = "listas" if screen_name == "detalle" else screen_name

    # ── Acciones (pendientes de implementar) ────────────────────────────
    def new_list(self):
        """Aquí se abrirá el flujo para crear una lista nueva."""

    # ── Progreso de la lista ────────────────────────────────────────────
    def refresh_progress(self):
        items = self.root.ids.sm.get_screen("detalle").ids.item_list.children
        total = len(items)
        done = sum(1 for item in items if item.done)
        self.total_items = total
        self.done_items = done
        self.progress = done / total if total else 0
        self.percent = int(round(self.progress * 100))


if __name__ == "__main__":
    ShoppingListApp().run()
