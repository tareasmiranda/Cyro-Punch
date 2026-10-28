"""
Lista de compras · Kivy + KivyMD
=================================

Pantallas:
  1. Inicio          (saludo + botón "Nueva lista")
  2. Listas          ("Mis listas" + una tarjeta por cada lista creada)
  3. Nueva / Editar  (formulario: nombre, comercio y tipo de lista)
  4. Detalle         (progreso + artículos con checkbox, o bloc de notas)
  5. Ajustes         (tema oscuro, notificaciones, idioma)

Funcionalidad:
  - Los botones "Nueva lista" (Inicio) y "Agregar" (Listas) abren el mismo
    formulario. Al crear la lista se abre su detalle.
  - Una lista puede ser "Checklist" (artículos que se marcan) o "Notepad"
    (texto libre). Se puede editar su nombre, comercio y tipo, agregar y
    quitar artículos, y eliminar la lista completa.
  - Todo se guarda en un archivo JSON ("listas.json") y se recupera al
    abrir la aplicación de nuevo. En escritorio queda junto a este archivo;
    en Android/iOS, en la carpeta de datos privada de la app.

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

import json
import os
import uuid
from datetime import date

from kivy.config import Config
from kivy.utils import platform

# En escritorio, la ventana simula el tamaño de un teléfono. Debe definirse
# ANTES de importar la ventana de Kivy (kivy.core.window).
if platform in ("win", "linux", "macosx"):
    Config.set("graphics", "width", "392")
    Config.set("graphics", "height", "800")

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.lang.builder import global_idmap
from kivy.logger import Logger
from kivy.metrics import Metrics, dp, sp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.widget import Widget
from kivy.utils import escape_markup, get_color_from_hex

from kivymd.app import MDApp

# Cuando aparece el teclado en el móvil, la interfaz se encoge para caber
# sobre él. Así el bloc de notas (que ocupa todo el alto) se ajusta al espacio
# que queda en vez de empujar toda la pantalla hacia arriba.
Window.softinput_mode = "resize"

# ─────────────────────────────────────────────────────────────────────────
#  Paleta de colores: modo oscuro (por defecto) y modo claro
# ─────────────────────────────────────────────────────────────────────────
# Ambos modos usan los mismos roles de color; el verde lima de acento y el
# color de texto sobre él son idénticos, solo cambian los tonos neutros.
PALETTE_DARK = {
    "BG": "#0A0B0F",  # fondo de pantalla
    "SURFACE": "#14161B",  # tarjetas y filas
    "SURFACE_ALT": "#1C1F26",  # botón atrás, ícono de la tarjeta, píldora activa
    "NAV_BG": "#0E1015",  # barra de navegación inferior
    "BORDER": "#23262E",  # borde de tarjetas
    "ACCENT": "#BEF24B",  # verde lima
    "ACCENT_FG": "#0A0B0F",  # texto/íconos sobre el verde lima
    "TEXT": "#FFFFFF",  # texto principal
    "MUTED": "#9599A4",  # texto secundario
    "SUBTLE": "#6E7280",  # íconos y etiquetas inactivas de la barra
    "TRACK": "#2A2D35",  # riel de la barra de progreso / interruptor apagado
    "CHECK_BORDER": "#7F8390",  # borde del checkbox vacío
}

PALETTE_LIGHT = {
    "BG": "#F5F6F8",
    "SURFACE": "#FFFFFF",
    "SURFACE_ALT": "#ECEEF2",
    "NAV_BG": "#FFFFFF",
    "BORDER": "#E1E3E8",
    "ACCENT": "#4AE236",
    "ACCENT_FG": "#0A0B0F",
    "TEXT": "#14161B",
    "MUTED": "#5B5F6B",
    "SUBTLE": "#8A8D96",
    "TRACK": "#DADDE3",
    "CHECK_BORDER": "#B5B8C0",
}


def mix(color_a, color_b, t):
    """Interpola entre dos colores RGBA (t = 0 → a, t = 1 → b)."""
    return [a + (b - a) * t for a, b in zip(color_a, color_b)]


# Nombres disponibles dentro del código KV (dp/sp y mix). Los colores del
# tema viven como propiedades de la App (app.bg_color, app.text_color...)
# para que el KV reaccione cuando se alterna entre modo oscuro y claro.
global_idmap.update({"dp": dp, "sp": sp, "mix": mix})


# ─────────────────────────────────────────────────────────────────────────
#  Textos de la interfaz (Español / Inglés)
# ─────────────────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "es": {
        "greeting": "Hola, ¿cómo va\ntu día?",
        "greeting_sub": "Empieza creando una lista y organiza\ntodo lo que necesites :)",
        "new_list": "Nueva lista",
        "my_lists": "Mis listas",
        "add": "Agregar",
        "active_list_one": "lista activa",
        "active_list_many": "listas activas",
        "updated_today": "Actualizada hoy",
        "updated_on": "Actualizada el {}",
        "items_completed": "{} artículos · {} completados",
        "completed_of": "{} de {} completados",
        "no_lists": "Aún no tienes listas",
        "no_lists_sub": "Crea la primera con el botón Agregar.",
        # Formulario
        "new_list_title": "Nueva lista",
        "new_list_sub": "Organiza tu próxima compra a tu manera.",
        "edit_list_title": "Editar lista",
        "edit_list_sub": "Cambia los datos de tu lista.",
        "list_name": "Nombre de la lista",
        "list_name_hint": "Ej: Compra semanal",
        "store": "Comercio",
        "store_hint": "Ej: Líder",
        "list_type": "Tipo de lista",
        "checklist": "Checklist",
        "checklist_desc": "Marca lo que ya compraste.",
        "notepad": "Notepad",
        "notepad_desc": "Escribe tus notas libremente.",
        "create_list": "Crear lista",
        "save_changes": "Guardar cambios",
        "cancel": "Cancelar",
        "delete_list": "Eliminar lista",
        "confirm_delete": "Toca de nuevo para eliminar",
        "info_new": "Después podrás agregar productos a tu nueva lista.",
        "info_edit": "Los cambios se guardan automáticamente en tu dispositivo.",
        # Detalle
        "add_product_hint": "Agregar producto",
        "price_hint": "$",
        "total_label": "Total de la compra",
        "notes_hint": "Escribe tus notas aquí...",
        # Ajustes
        "settings": "Ajustes",
        "settings_sub": "Personaliza tu experiencia de compra.",
        "dark_mode": "Tema oscuro",
        "notifications": "Notificaciones",
        "language": "Idioma",
        "language_name": "Español",
        "nav_home": "Inicio",
        "nav_lists": "Listas",
        "nav_settings": "Ajustes",
    },
    "en": {
        "greeting": "Hey, how's\nyour day?",
        "greeting_sub": "Start making a list and organize\neverything you need :)",
        "new_list": "New list",
        "my_lists": "My lists",
        "add": "Add",
        "active_list_one": "active list",
        "active_list_many": "active lists",
        "updated_today": "Updated today",
        "updated_on": "Updated on {}",
        "items_completed": "{} items · {} completed",
        "completed_of": "{} of {} completed",
        "no_lists": "You have no lists yet",
        "no_lists_sub": "Create your first one with the Add button.",
        # Form
        "new_list_title": "New list",
        "new_list_sub": "Organize your next shop your own way.",
        "edit_list_title": "Edit list",
        "edit_list_sub": "Change your list details.",
        "list_name": "List name",
        "list_name_hint": "E.g. Weekly shop",
        "store": "Store",
        "store_hint": "E.g. Lider",
        "list_type": "List type",
        "checklist": "Checklist",
        "checklist_desc": "Tick off what you bought.",
        "notepad": "Notepad",
        "notepad_desc": "Write your notes freely.",
        "create_list": "Create list",
        "save_changes": "Save changes",
        "cancel": "Cancel",
        "delete_list": "Delete list",
        "confirm_delete": "Tap again to delete",
        "info_new": "You can add products to your new list afterwards.",
        "info_edit": "Changes are saved automatically on your device.",
        # Detail
        "add_product_hint": "Add product",
        "price_hint": "$",
        "total_label": "Shopping total",
        "notes_hint": "Write your notes here...",
        # Settings
        "settings": "Settings",
        "settings_sub": "Customize your shopping experience.",
        "dark_mode": "Dark mode",
        "notifications": "Notifications",
        "language": "Language",
        "language_name": "English",
        "nav_home": "Home",
        "nav_lists": "Lists",
        "nav_settings": "Settings",
    },
}

WEEKDAYS = {
    "es": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
}
MONTHS = {
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
           "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
}


def format_date(iso, lang, weekday=True):
    """Convierte una fecha ISO en texto legible según el idioma."""
    try:
        d = date.fromisoformat(str(iso)[:10])
    except ValueError:
        return str(iso)
    lang = lang if lang in MONTHS else "es"
    month = MONTHS[lang][d.month - 1]
    if lang == "es":
        text = f"{d.day} de {month}"
    else:
        text = f"{month} {d.day}"
    if weekday:
        text = f"{WEEKDAYS[lang][d.weekday()]}, {text}"
    return text


def clean_price(value):
    """Deja solo los dígitos de un precio (pesos, sin decimales)."""
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def format_price(value):
    """1990 → "$1.990" (separador de miles con punto). Vacío si no hay precio."""
    digits = clean_price(value)
    if not digits:
        return ""
    return "$" + f"{int(digits):,}".replace(",", ".")


# ─────────────────────────────────────────────────────────────────────────
#  Persistencia (archivo JSON)
# ─────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILENAME = "listas.json"
LIST_TYPES = ("checklist", "notepad")

# Ruta al archivo .kv que define el diseño y la jerarquía visual.
KV_PATH = os.path.join(BASE_DIR, "interfaz.kv")


def normalize_list(raw):
    """Valida una lista leída del JSON y completa lo que falte.

    Devuelve None si el dato no se puede aprovechar. Así un archivo
    editado a mano o dañado parcialmente no rompe la aplicación.
    """
    if not isinstance(raw, dict):
        return None
    today = date.today().isoformat()
    items = []
    raw_items = raw.get("items")
    if isinstance(raw_items, list):
        for it in raw_items:
            if isinstance(it, dict) and str(it.get("title", "")).strip():
                items.append(
                    {
                        "title": str(it["title"]),
                        # Las listas guardadas con "quantity" (versión anterior)
                        # quedan sin precio: una cantidad no es un precio.
                        "price": clean_price(it.get("price", "")),
                        "done": bool(it.get("done", False)),
                    }
                )
    kind = raw.get("type")
    return {
        "id": str(raw.get("id") or uuid.uuid4().hex),
        "name": str(raw.get("name") or "").strip() or "Lista",
        "store": str(raw.get("store") or "").strip(),
        "type": kind if kind in LIST_TYPES else "checklist",
        "created": str(raw.get("created") or today),
        "updated": str(raw.get("updated") or today),
        "items": items,
        "notes": str(raw.get("notes") or ""),
    }


# ─────────────────────────────────────────────────────────────────────────
#  Tipografía
# ─────────────────────────────────────────────────────────────────────────
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


class FormButton(Pressable, AnchorLayout):
    """Botón verde lima de ancho completo (p. ej. "Crear lista")."""

    text = StringProperty()
    icon = StringProperty("check")


class AddButton(Pressable, AnchorLayout):
    """Botón cuadrado verde lima con un ícono (agregar artículo)."""

    icon = StringProperty("plus")


class LinkButton(Pressable, AnchorLayout):
    """Botón de solo texto (Cancelar, Eliminar lista)."""

    text = StringProperty()
    tint = ColorProperty([1, 1, 1, 1])


class IconButton(Pressable, AnchorLayout):
    """Botón cuadrado redondeado con un ícono (p. ej. el botón atrás)."""

    icon = StringProperty("arrow-left")


class DeleteButton(Pressable, AnchorLayout):
    """Pequeña "x" al final de cada artículo para quitarlo."""


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


class FieldBase(Card):
    """Base de los campos de texto: el texto vive en `text`."""

    text = StringProperty()
    hint = StringProperty()
    error = BooleanProperty(False)

    __events__ = ("on_submit",)

    def on_submit(self):
        """Se dispara al presionar Enter dentro del campo."""


class InputField(FieldBase):
    """Campo de texto con ícono a la izquierda (formulario)."""

    icon = StringProperty("format-list-bulleted")


class QuickInput(FieldBase):
    """Campo de texto compacto, sin ícono (fila de agregar artículo).

    Con `numeric: True` solo acepta dígitos (y abre el teclado numérico).
    """

    numeric = BooleanProperty(False)


class TypeOption(Pressable, Card):
    """Opción de tipo de lista (Checklist / Notepad) con botón de radio."""

    key = StringProperty()
    icon = StringProperty()
    title = StringProperty()
    desc = StringProperty()
    selected = BooleanProperty(False)


class ListCard(TapCard):
    """Tarjeta de una lista en la pantalla "Mis listas"."""

    list_id = StringProperty()
    name = StringProperty()
    subtitle = StringProperty()
    meta = StringProperty()
    icon = StringProperty("basket-outline")


class EmptyState(BoxLayout):
    """Mensaje que se muestra mientras no existe ninguna lista."""


class ShoppingItem(Pressable, Card):
    """Fila de un artículo: casilla, nombre, precio y botón para quitarlo."""

    title = StringProperty()
    price = StringProperty()  # solo dígitos, tal como se guarda en el JSON
    price_text = StringProperty()  # "$1.990", lo que se muestra
    done = BooleanProperty(False)
    title_markup = StringProperty()
    item = ObjectProperty(None, allownone=True)  # diccionario guardado en el JSON

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sync_title()
        self.price_text = format_price(self.price)

    def on_price(self, *_):
        self.price_text = format_price(self.price)

    def on_title(self, *_):
        self._sync_title()

    def on_done(self, *_):
        self._sync_title()

    def on_release(self):
        self.done = not self.done
        if self.item is not None:
            self.item["done"] = self.done
        app = MDApp.get_running_app()
        if app is not None:
            app.items_changed()

    def _sync_title(self):
        text = escape_markup(self.title)
        self.title_markup = f"[s]{text}[/s]" if self.done else text


class LangOption(Pressable, BoxLayout):
    """Una opción dentro del menú desplegable de idioma."""

    code = StringProperty()
    label = StringProperty()
    selected = BooleanProperty(False)


class LanguageDropDown(DropDown):
    """Menú desplegable con los idiomas disponibles (Español / English).

    Su contenido (las dos opciones) se define en interfaz.kv. Se abre
    alineado al borde derecho del widget que lo invoca, con un breve
    desvanecimiento + deslizamiento hacia su posición final.
    """

    def _reposition(self, *args):
        super()._reposition(*args)
        if self.attach_to is None:
            return
        # El comportamiento por defecto alinea el menú al borde IZQUIERDO
        # del widget ancla; lo recorremos para que quede pegado al borde
        # DERECHO (donde están el texto del idioma actual y la flecha).
        right_edge = self.attach_to.to_window(self.attach_to.right, 0)[0]
        x = right_edge - self.width
        self.x = max(x, 0)

    def open(self, widget):
        super().open(widget)
        target_y = self.y
        self.y = target_y + dp(10)
        self.opacity = 0
        Animation(y=target_y, opacity=1, duration=0.16, t="out_quad").start(self)


# ─────────────────────────────────────────────────────────────────────────
#  Aplicación
# ─────────────────────────────────────────────────────────────────────────
class ShoppingListApp(MDApp):
    font_name = StringProperty("Roboto")
    current_tab = StringProperty("inicio")  # pestaña resaltada en la barra
    lang = StringProperty("es")  # "es" o "en"
    theme_dark = BooleanProperty(True)  # True = oscuro, False = claro

    # Resumen de listas (pantalla "Mis listas")
    lists_count = NumericProperty(0)

    # Lista abierta en la pantalla de detalle
    detail_name = StringProperty("")
    detail_meta = StringProperty("")
    detail_kind = StringProperty("checklist")
    detail_notes = StringProperty("")
    total_items = NumericProperty(0)
    done_items = NumericProperty(0)
    progress = NumericProperty(0)  # 0..1
    percent = NumericProperty(0)  # 0..100
    total_text = StringProperty("$0")  # total de la compra, p. ej. "$7.770"
    new_item_name = StringProperty("")
    new_item_price = StringProperty("")

    # Formulario de crear / editar lista
    form_mode = StringProperty("new")  # "new" o "edit"
    form_name = StringProperty("")
    form_store = StringProperty("")
    form_type = StringProperty("checklist")
    delete_armed = BooleanProperty(False)  # ya se tocó una vez "Eliminar lista"

    # Colores del tema activo (arrancan en modo oscuro). El KV los usa como
    # app.xxx_color; al alternar el tema se animan hacia la otra paleta.
    bg_color = ColorProperty(get_color_from_hex(PALETTE_DARK["BG"]))
    surface_color = ColorProperty(get_color_from_hex(PALETTE_DARK["SURFACE"]))
    surface_alt_color = ColorProperty(get_color_from_hex(PALETTE_DARK["SURFACE_ALT"]))
    nav_bg_color = ColorProperty(get_color_from_hex(PALETTE_DARK["NAV_BG"]))
    border_color = ColorProperty(get_color_from_hex(PALETTE_DARK["BORDER"]))
    accent_color = ColorProperty(get_color_from_hex(PALETTE_DARK["ACCENT"]))
    accent_fg_color = ColorProperty(get_color_from_hex(PALETTE_DARK["ACCENT_FG"]))
    text_color = ColorProperty(get_color_from_hex(PALETTE_DARK["TEXT"]))
    muted_color = ColorProperty(get_color_from_hex(PALETTE_DARK["MUTED"]))
    subtle_color = ColorProperty(get_color_from_hex(PALETTE_DARK["SUBTLE"]))
    track_color = ColorProperty(get_color_from_hex(PALETTE_DARK["TRACK"]))
    check_border_color = ColorProperty(get_color_from_hex(PALETTE_DARK["CHECK_BORDER"]))

    SCREEN_ORDER = ("inicio", "listas", "detalle", "ajustes")

    def build(self):
        self.title = "Lista de compras"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Lime"
        self.font_name = register_fonts()
        Window.clearcolor = self.bg_color
        Window.bind(on_keyboard=self._on_keyboard)
        Window.bind(on_resize=lambda *_: self._schedule_ui_check())

        self.data_file = self._data_path()
        self.lists = self.load_lists()
        self.current_id = None
        self._form_origin = "listas"
        self._disarm_event = None
        root = Builder.load_file(KV_PATH)
        # Cuerpo del detalle: se crean ambos, pero en pantalla hay siempre uno
        # solo (ver _show_body). Así no se depende de ocultar widgets con
        # tamaño 0, opacidad o "disabled".
        self.items_scroll = Factory.ItemsScroll()
        self.notes_card = Factory.NotesCard()
        return root

    def on_start(self):
        sm = self.root.ids.sm
        sm.transition = SlideTransition(duration=0.2)
        self.refresh_lists()

    def on_pause(self):
        self.save_now()
        return True  # permite que la app siga viva en segundo plano (Android)

    def on_resume(self):
        # Al volver de segundo plano se revisa que la interfaz esté sana.
        self.refresh_lists()
        self.ui_check()

    def on_stop(self):
        self.save_now()

    # ── Persistencia ────────────────────────────────────────────────────
    def _data_path(self):
        """Dónde vive el JSON: carpeta privada en móvil, junto al código en PC."""
        if platform in ("android", "ios"):
            folder = self.user_data_dir
        else:
            folder = BASE_DIR
        return os.path.join(folder, DATA_FILENAME)

    def load_lists(self):
        """Lee las listas guardadas. Sin archivo (o dañado) arranca vacío."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
            Logger.error(f"Listas: no se pudo leer {self.data_file}: {exc}")
            # Se conserva una copia del archivo dañado para no perder datos.
            try:
                os.replace(self.data_file, self.data_file + ".dañado")
            except OSError:
                pass
            return []
        raw_lists = data.get("lists", []) if isinstance(data, dict) else []
        lists = [normalize_list(raw) for raw in raw_lists]
        return [lst for lst in lists if lst is not None]

    def save_now(self, *_):
        """Escribe todas las listas en el JSON (escritura atómica)."""
        Clock.unschedule(self.save_now)
        payload = {"version": 1, "lists": self.lists}
        tmp_path = self.data_file + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.data_file)
        except OSError as exc:
            Logger.error(f"Listas: no se pudo guardar {self.data_file}: {exc}")

    def schedule_save(self, delay=0.6):
        """Guarda poco después; útil mientras se escribe en el bloc de notas."""
        Clock.unschedule(self.save_now)
        Clock.schedule_once(self.save_now, delay)

    # ── Acceso a las listas ─────────────────────────────────────────────
    def get_list(self, list_id):
        for lst in self.lists:
            if lst["id"] == list_id:
                return lst
        return None

    def current_list(self):
        return self.get_list(self.current_id) if self.current_id else None

    @staticmethod
    def _touch(lst):
        lst["updated"] = date.today().isoformat()

    # ── Navegación ──────────────────────────────────────────────────────
    def go(self, screen_name):
        sm = self.root.ids.sm
        if sm.current == screen_name:
            return
        Window.release_all_keyboards()
        if screen_name == "nueva":
            direction = "up"  # el formulario sube como una ventana
        elif sm.current == "nueva":
            direction = "down"
        else:
            order = self.SCREEN_ORDER
            forward = order.index(screen_name) > order.index(sm.current)
            direction = "left" if forward else "right"
        sm.transition.direction = direction
        sm.current = screen_name
        self._schedule_ui_check()
        # El detalle y el formulario pertenecen a la pestaña "Listas".
        self.current_tab = "listas" if screen_name in ("detalle", "nueva") else screen_name

    def _on_keyboard(self, _window, key, *_args):
        """Tecla "atrás" de Android / Esc: cierra el formulario o el detalle."""
        if key != 27:
            return False
        current = self.root.ids.sm.current
        if current == "nueva":
            self.cancel_form()
            return True
        if current == "detalle":
            self.go("listas")
            return True
        return False

    # ── Formulario: crear y editar ──────────────────────────────────────
    def open_form_new(self):
        """Abre el formulario vacío (botones "Nueva lista" y "Agregar")."""
        self.form_mode = "new"
        self.form_name = ""
        self.form_store = ""
        self.form_type = "checklist"
        self._open_form()

    def open_form_edit(self):
        """Abre el formulario con los datos de la lista que se está viendo."""
        lst = self.current_list()
        if lst is None:
            return
        self.form_mode = "edit"
        self.form_name = lst["name"]
        self.form_store = lst["store"]
        self.form_type = lst["type"]
        self._open_form()

    def _open_form(self):
        sm = self.root.ids.sm
        if sm.current != "nueva":
            self._form_origin = sm.current
        self._disarm_delete()
        sm.get_screen("nueva").ids.name_field.error = False
        self.go("nueva")

    def cancel_form(self):
        self._disarm_delete()
        self.go(self._form_origin or "listas")

    def submit_form(self):
        """Crea la lista nueva o guarda los cambios de la que se edita."""
        name = self.form_name.strip()
        if not name:
            self.root.ids.sm.get_screen("nueva").ids.name_field.error = True
            return
        store = self.form_store.strip()
        self._disarm_delete()

        if self.form_mode == "edit":
            lst = self.current_list()
            if lst is None:
                return
            lst["name"] = name
            lst["store"] = store
            # El tipo de lista no se cambia al editar (se elige solo al crear).
            self._touch(lst)
            self.save_now()
            self.refresh_lists()
            self._load_detail(lst)
            self.go("detalle")
            return

        today = date.today().isoformat()
        lst = {
            "id": uuid.uuid4().hex,
            "name": name,
            "store": store,
            "type": self.form_type,
            "created": today,
            "updated": today,
            "items": [],
            "notes": "",
        }
        self.lists.append(lst)
        self.save_now()
        self.refresh_lists()
        self.open_list(lst["id"])

    def request_delete(self):
        """Elimina la lista actual; pide tocar dos veces para confirmar."""
        if not self.delete_armed:
            self.delete_armed = True
            self._disarm_event = Clock.schedule_once(self._disarm_delete, 3)
            return
        self._disarm_delete()
        lst = self.current_list()
        if lst is not None:
            self.lists = [other for other in self.lists if other is not lst]
        self.current_id = None
        self.save_now()
        self.refresh_lists()
        self.go("listas")

    def _disarm_delete(self, *_):
        if self._disarm_event is not None:
            self._disarm_event.cancel()
            self._disarm_event = None
        self.delete_armed = False

    # ── Pantalla "Mis listas" ───────────────────────────────────────────
    def _list_subtitle(self, lst):
        if lst["type"] == "notepad":
            return self.tr(self.lang, "notepad")
        total = len(lst["items"])
        done = sum(1 for it in lst["items"] if it["done"])
        return self.tr(self.lang, "items_completed").format(total, done)

    def _list_meta(self, lst):
        if lst["updated"][:10] == date.today().isoformat():
            when = self.tr(self.lang, "updated_today")
        else:
            when = self.tr(self.lang, "updated_on").format(
                format_date(lst["updated"], self.lang, weekday=False)
            )
        return f"{lst['store']} · {when}" if lst["store"] else when

    def refresh_lists(self):
        """Reconstruye las tarjetas de "Mis listas" (la más nueva arriba)."""
        box = self.root.ids.sm.get_screen("listas").ids.lists_box
        box.clear_widgets()
        self.lists_count = len(self.lists)
        if not self.lists:
            box.add_widget(EmptyState())
            return
        for lst in reversed(self.lists):
            box.add_widget(
                ListCard(
                    list_id=lst["id"],
                    name=lst["name"],
                    subtitle=self._list_subtitle(lst),
                    meta=self._list_meta(lst),
                    icon="note-edit-outline" if lst["type"] == "notepad" else "basket-outline",
                )
            )

    # ── Pantalla de detalle ─────────────────────────────────────────────
    def open_list(self, list_id):
        lst = self.get_list(list_id)
        if lst is None:
            return
        self._load_detail(lst)
        self.go("detalle")

    def _refresh_detail_meta(self, lst):
        created = format_date(lst["created"], self.lang)
        self.detail_meta = f"{lst['store']} · {created}" if lst["store"] else created

    def _load_detail(self, lst, check=True):
        # current_id va primero: así, al cambiar el texto del bloc de notas,
        # set_notes() ya compara contra la lista correcta.
        self.current_id = lst["id"]
        self.detail_name = lst["name"]
        self.detail_kind = lst["type"]
        self.detail_notes = lst["notes"]
        self.new_item_name = ""
        self.new_item_price = ""
        self._refresh_detail_meta(lst)

        scroll, box = self._items_widgets()
        box.clear_widgets()
        for it in lst["items"]:
            box.add_widget(
                ShoppingItem(
                    title=it["title"], price=it["price"], done=it["done"], item=it
                )
            )
        self._show_body(lst["type"])
        scroll.scroll_y = 1  # siempre se empieza mirando arriba
        self.refresh_progress()
        if check:
            self._schedule_ui_check()

    def add_item(self):
        lst = self.current_list()
        name = self.new_item_name.strip()
        if lst is None or not name:
            return
        item = {"title": name, "price": clean_price(self.new_item_price), "done": False}
        lst["items"].append(item)

        self._items_widgets()[1].add_widget(
            ShoppingItem(title=item["title"], price=item["price"], item=item)
        )
        self.new_item_name = ""
        self.new_item_price = ""
        self.items_changed()
        # Baja hasta el artículo recién agregado, pero solo si la lista ya
        # no cabe en pantalla (si cabe, debe quedarse pegada arriba).
        Clock.schedule_once(self._scroll_items_to_end, 0.05)

    def _items_widgets(self):
        return self.items_scroll, self.items_scroll.ids.item_list

    def _show_body(self, kind):
        """Deja en el cuerpo del detalle solo lo que corresponde al tipo de lista."""
        body = self.root.ids.sm.get_screen("detalle").ids.body
        wanted = self.items_scroll if kind == "checklist" else self.notes_card
        unwanted = self.notes_card if kind == "checklist" else self.items_scroll
        # Se comprueba con body.children: widget.parent devuelve un proxy débil
        # y compararlo con "is" no funciona.
        if unwanted in body.children:
            body.remove_widget(unwanted)
        if wanted not in body.children:
            body.add_widget(wanted)

    def _scroll_items_to_end(self, *_):
        scroll, box = self._items_widgets()
        content = box.minimum_height
        if content > scroll.height:
            scroll.scroll_y = 0  # baja hasta el último artículo

    # ── Autorreparación de la interfaz ──────────────────────────────────
    def _schedule_ui_check(self, *_):
        """Programa una revisión poco después de que termine la transición."""
        if self.root is None or "sm" not in self.root.ids:
            return
        Clock.unschedule(self.ui_check)
        Clock.schedule_once(self.ui_check, self.root.ids.sm.transition.duration + 0.35)

    @staticmethod
    def _hit_path(widget, x, y):
        """Cadena de widgets que recibiría un toque en (x, y) de la ventana.

        Replica Widget.on_touch_down: un widget deshabilitado que contiene el
        punto se queda con el toque aunque sea invisible.
        """
        lx, ly = widget.to_widget(x, y)
        if not widget.collide_point(lx, ly):
            return None
        if widget.disabled:
            return [widget]
        for child in widget.children[:]:
            path = ShoppingListApp._hit_path(child, x, y)
            if path:
                return [widget] + path
        return [widget]

    @staticmethod
    def _describe(widget):
        x, y = widget.to_window(*widget.pos)
        return (f"{widget.__class__.__name__}(pos=({x:.0f},{y:.0f}), "
                f"size=({widget.width:.0f},{widget.height:.0f}), "
                f"opacity={getattr(widget, 'opacity', 1)}, disabled={widget.disabled})")

    def ui_check(self, *_):
        """Detecta y repara una pantalla del detalle "rota".

        Síntoma que se buscaba: la lista del detalle no se ve y los botones
        de arriba (editar, volver) no responden hasta reiniciar la app. Se
        revisa que no haya una transición activa ni pantallas de más, que un
        toque sobre el botón "volver" lo reciba ese botón y que, si la lista
        tiene artículos, se vea alguno. Si algo falla, se reconstruye el
        detalle y se deja en la consola una línea "UI auto-reparada: ..." con
        el detalle de qué se encontró (por ejemplo, qué widget tapaba el botón).
        """
        if self.root is None or "sm" not in self.root.ids:
            return
        sm = self.root.ids.sm
        found = []
        if sm.transition.is_active:
            # Normal si se acaba de cambiar de pantalla: se espera a que
            # termine. Solo si sigue activa tras varios intentos se corta.
            self._ui_waits = getattr(self, "_ui_waits", 0) + 1
            if self._ui_waits < 4:
                Clock.schedule_once(self.ui_check, 0.4)
                return
            sm.transition.stop()
            found.append("transición activa (colgada)")
        self._ui_waits = 0
        current = sm.current_screen
        if current is not None:
            for screen in list(sm.children):
                if screen is not current:
                    sm.real_remove_widget(screen)
                    found.append(f"pantalla sobrante '{screen.name}'")
            if current not in sm.children:
                sm.real_add_widget(current)
                found.append(f"pantalla '{current.name}' no estaba en pantalla")
            if abs(current.x - sm.x) > 1 or abs(current.y - sm.y) > 1:
                found.append(f"pantalla desplazada {tuple(round(v) for v in current.pos)}")
            current.pos = sm.pos
            current.opacity = 1

        lst = self.current_list()
        if sm.current == "detalle" and lst is not None:
            detail = sm.get_screen("detalle")
            # 1) ¿Un toque sobre los botones de arriba llega a esos botones?
            for button in (w for w in detail.walk() if isinstance(w, IconButton)):
                x, y = button.to_window(*button.center)
                path = self._hit_path(self.root, x, y)
                if path and button not in path:
                    found.append(
                        f"un toque sobre el botón '{button.icon}' lo recibe "
                        f"{self._describe(path[-1])}"
                    )
            # 2) ¿Se ve algún artículo dentro del área de la lista?
            if lst["type"] == "checklist" and lst["items"]:
                scroll, box = self._items_widgets()
                sx, sy = scroll.to_window(*scroll.pos)
                visible = False
                for row in box.children:
                    rx, ry = row.to_window(*row.pos)
                    if ry < sy + scroll.height and ry + row.height > sy:
                        visible = True
                        break
                if not visible or scroll.height < dp(60):
                    body = detail.ids.body
                    found.append(
                        "lista sin artículos visibles: "
                        f"scroll={self._describe(scroll)} size_hint_y={scroll.size_hint_y}, "
                        f"contenedor={self._describe(body)}, contenido={self._describe(box)}, "
                        f"scroll_y={scroll.scroll_y:.2f}, ventana={tuple(Window.size)}, "
                        f"densidad={Metrics.density}"
                    )
            if found:
                # Reconstruye el detalle desde los datos guardados y fuerza el
                # layout; una sola vez (sin reprogramar otra revisión).
                self._load_detail(lst, check=False)
                scroll, box = self._items_widgets()
                scroll.size_hint_y = 1
                detail.ids.body.do_layout()
                box.do_layout()
                scroll.scroll_y = 1
                Clock.schedule_once(self._after_repair, 0.4)
        if found:
            Logger.warning("Listas: UI auto-reparada: " + "; ".join(found))

    def _after_repair(self, *_):
        """Comprueba, una sola vez, si la reparación dejó la lista visible."""
        lst = self.current_list()
        if lst is None or lst["type"] != "checklist" or not lst["items"]:
            return
        scroll, _box = self._items_widgets()
        if scroll.height < dp(60):
            Logger.warning(
                "Listas: la reparación no bastó, la lista sigue sin alto: "
                f"{self._describe(scroll)} size_hint_y={scroll.size_hint_y}"
            )
        else:
            Logger.info("Listas: la lista volvió a verse tras la reparación")

    def delete_item(self, widget):
        lst = self.current_list()
        if lst is None:
            return
        for index, it in enumerate(lst["items"]):
            if it is widget.item:
                del lst["items"][index]
                break
        widget.parent.remove_widget(widget)
        self.items_changed()

    def items_changed(self):
        """Se llama al marcar, agregar o quitar un artículo."""
        lst = self.current_list()
        if lst is not None:
            self._touch(lst)
        self.refresh_progress()
        self.save_now()
        self.refresh_lists()

    def set_notes(self, text):
        """Guarda el texto del bloc de notas (con un pequeño retraso)."""
        lst = self.current_list()
        if lst is None or lst["type"] != "notepad" or lst["notes"] == text:
            return
        lst["notes"] = text
        self.detail_notes = text
        self._touch(lst)
        self.schedule_save()

    def refresh_progress(self):
        lst = self.current_list()
        items = lst["items"] if lst else []
        total = len(items)
        done = sum(1 for it in items if it["done"])
        self.total_items = total
        self.done_items = done
        self.total_text = format_price(sum(int(clean_price(it["price"]) or 0) for it in items)) or "$0"
        self.progress = done / total if total else 0
        self.percent = int(round(self.progress * 100))

    # ── Tema oscuro / claro ──────────────────────────────────────────────
    def set_dark_mode(self, active):
        """Alterna entre modo oscuro y claro con una transición suave."""
        if active == self.theme_dark:
            return
        self.theme_dark = active
        self.theme_cls.theme_style = "Dark" if active else "Light"
        palette = PALETTE_DARK if active else PALETTE_LIGHT
        # "TEXT" va primero a propósito: varios widgets (el texto de los
        # botones, el check del menú de idioma, etc.) fijan su color con
        # app.accent_color/app.accent_fg_color en vez del app.text_color
        # por defecto. Kivy mantiene ambos enlaces activos, así que si
        # "TEXT" se animara después, su valor ganaría en cada fotograma y
        # esos textos se verían blancos/negros en vez de su color propio.
        # Animando "TEXT" primero, el color específico de cada widget es
        # siempre el último en aplicarse.
        order = ["TEXT"] + [name for name in palette if name != "TEXT"]
        targets = {
            f"{name.lower()}_color": get_color_from_hex(palette[name])
            for name in order
        }
        Animation.cancel_all(self, *targets.keys())
        Animation(duration=0.35, t="out_quad", **targets).start(self)

    def on_bg_color(self, _instance, value):
        # Mantiene el fondo de la ventana sincronizado con la interfaz.
        Window.clearcolor = value

    # ── Idioma ───────────────────────────────────────────────────────────
    def tr(self, lang, key):
        """Traduce `key` al idioma indicado.

        Se llama desde el KV como app.tr(app.lang, "clave"): pasar
        app.lang explícitamente permite que los bindings de KV detecten
        la dependencia y actualicen el texto automáticamente al elegir
        un idioma distinto en el menú.
        """
        return TRANSLATIONS.get(lang, TRANSLATIONS["es"]).get(key, key)

    def set_language(self, code):
        """Cambia el idioma activo (llamado al elegir una opción del menú)."""
        if code in TRANSLATIONS:
            self.lang = code

    def on_lang(self, *_):
        # Los textos generados desde Python (tarjetas, fechas) se rehacen.
        if self.root is None:
            return
        self.refresh_lists()
        lst = self.current_list()
        if lst is not None:
            self._refresh_detail_meta(lst)

    def open_language_menu(self, anchor):
        """Abre el menú desplegable de idiomas anclado a `anchor`."""
        LanguageDropDown().open(anchor)


if __name__ == "__main__":
    ShoppingListApp().run()
