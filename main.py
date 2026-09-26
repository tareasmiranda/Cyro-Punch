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

Este archivo contiene la lógica de negocio y el backend de la app.
El diseño visual y la jerarquía de widgets viven en "interfaz.kv",
que se carga desde el método build() de la aplicación.
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

# Ruta al archivo .kv que define el diseño y la jerarquía visual.
KV_PATH = os.path.join(BASE_DIR, "interfaz.kv")


def register_fonts():
    """Usa Inter si está en ./fonts; de lo contrario, Roboto (incluida)."""
    regular = os.path.join(BASE_DIR, "fonts", "Inter-Regular.ttf")
    bold = os.path.join(BASE_DIR, "fonts", "Inter-Bold.ttf")
    if os.path.exists(regular) and os.path.exists(bold):
        LabelBase.register(name="Inter", fn_regular=regular, fn_bold=bold)
        return "Inter"
    return "Roboto"


# ─────────────────────────────────────────────────────────────────────────
#  Widgets reutilizables (el estilo está definido en interfaz.kv)
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
        return Builder.load_file(KV_PATH)

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
