"""
Lista de compras · Kivy + KivyMD
=================================

Pantallas:
  1. Login / Registro  (crear cuenta o iniciar sesión)
  2. Inicio            (saludo + botón "Nueva lista")
  3. Listas            ("Mis listas" + una tarjeta por cada lista)
  4. Nueva / Editar    (formulario: nombre, comercio y tipo de lista)
  5. Detalle           (progreso + artículos, o bloc de notas)
  6. Ajustes           (tema, notificaciones, idioma, precios, cerrar sesión)
  7. Precios más bajos (historial global por comercio, con borrado por fila)

Autenticación y cuentas:
  - Los usuarios se guardan en "usuarios.json" (PBKDF2-SHA256 + salt).
  - La pantalla de login alterna entre dos modos:
      · "login"    → iniciar sesión con una cuenta existente
      · "register" → crear una cuenta nueva
    Al pie hay un enlace para cambiar de un modo al otro.
  - Cada cuenta tiene SU PROPIO archivo de listas:
        listas_<usuario>.json
    así las listas de un usuario no se mezclan con las de otro.

Precios globales por comercio:
  - Cada vez que se agrega un artículo con precio a una lista cuyo comercio
    está definido, el precio se guarda en "precios_globales.json" bajo la
    clave normalizada del nombre del artículo:
        { "items": { "leche": { "Lider": 1500, "Jumbo": 1200 } } }
  - Si al agregar el artículo otro comercio ya lo tenía MÁS BARATO, se
    muestra una notificación local con el comercio y precio más baratos,
    y la fila muestra un aviso "Más barato en X: $Y".
  - En "Mis listas", cada tarjeta añade "· ahorras hasta $Z" cuando hay
    artículos pendientes que se podrían comprar más baratos en otro
    comercio conocido.
  - En Ajustes → "Precios más bajos" se puede ver y borrar cada precio
    individual del historial global.
  - En Ajustes → "Borrar historial de precios" se puede borrar todo
    (con confirmación de 2 toques).

Instalación:
    pip install kivy kivymd plyer pyjnius
    Windows:  pip install winotify   (o win10toast)
    Linux:    sudo apt install libnotify-bin
"""

import hashlib
import json
import os
import re
import secrets
import shutil
import uuid
import time
from datetime import date, datetime

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

from noti import notify_cheaper_store, notify_test

# El teclado en pantalla debe EMPUJAR hacia arriba el contenido (en vez de
# aplastar el layout) para que la barra de agregar producto en el detalle
# quede visible por encima del teclado.
Window.softinput_mode = "below_target"

# ─────────────────────────────────────────────────────────────────────────
#  Paletas de color
# ─────────────────────────────────────────────────────────────────────────
PALETTE_DARK = {
    "BG": "#0A0B0F",
    "SURFACE": "#14161B",
    "SURFACE_ALT": "#1C1F26",
    "NAV_BG": "#0E1015",
    "BORDER": "#23262E",
    "ACCENT": "#BEF24B",
    "ACCENT_FG": "#0A0B0F",
    "TEXT": "#FFFFFF",
    "MUTED": "#9599A4",
    "SUBTLE": "#6E7280",
    "TRACK": "#2A2D35",
    "CHECK_BORDER": "#7F8390",
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
    return [a + (b - a) * t for a, b in zip(color_a, color_b)]


global_idmap.update({"dp": dp, "sp": sp, "mix": mix})


# ─────────────────────────────────────────────────────────────────────────
#  Textos de la interfaz
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
        "new_list_title": "Nueva lista",
        "new_list_sub": "Organiza tu próxima compra a tu manera.",
        "edit_list_title": "Editar lista",
        "edit_list_sub": "Cambia los datos de tu lista.",
        "list_name": "Nombre de la lista",
        "list_name_hint": "Ej: Compra semanal",
        "store": "Comercio",
        "store_hint": "Ej: Lider",
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
        "add_product_hint": "Agregar producto",
        "price_hint": "$",
        "total_label": "Total de la compra",
        "notes_hint": "Escribe tus notas aquí...",
        "settings": "Ajustes",
        "settings_sub": "Personaliza tu experiencia de compra.",
        "dark_mode": "Tema oscuro",
        "notifications": "Notificaciones",
        "language": "Idioma",
        "language_name": "Español",
        "clear_prices": "Borrar historial de precios",
        "clear_prices_confirm": "Toca de nuevo para borrar",
        "nav_home": "Inicio",
        "nav_lists": "Listas",
        "nav_settings": "Ajustes",
        # Login / Registro
        "login_title": "Bienvenido",
        "login_subtitle_login": "Inicia sesión para ver tus listas",
        "login_subtitle_register": "Crea tu cuenta para empezar",
        "username_hint": "Usuario",
        "password_hint": "Contraseña",
        "login": "Iniciar sesión",
        "create_account": "Crear cuenta",
        "switch_to_register": "Crear cuenta nueva",
        "switch_to_login": "Ya tengo cuenta · Iniciar sesión",
        "logout": "Cerrar sesión",
        "auth_empty": "Completa usuario y contraseña.",
        "auth_user_not_found": "Usuario no encontrado.",
        "auth_wrong_password": "Contraseña incorrecta.",
        "auth_user_exists": "Ese usuario ya existe.",
        # Precios más bajos
        "lowest_prices": "Precios más bajos",
        "lowest_prices_sub": "Historial por comercio",
        "no_prices": "Sin precios registrados",
        "no_prices_sub": "Los precios se guardan al agregar productos con precio a una lista con comercio.",
        "lowest_price_label": "Precio más bajo",
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
        "add_product_hint": "Add product",
        "price_hint": "$",
        "total_label": "Shopping total",
        "notes_hint": "Write your notes here...",
        "settings": "Settings",
        "settings_sub": "Customize your shopping experience.",
        "dark_mode": "Dark mode",
        "notifications": "Notifications",
        "language": "Language",
        "language_name": "English",
        "clear_prices": "Clear price history",
        "clear_prices_confirm": "Tap again to clear",
        "nav_home": "Home",
        "nav_lists": "Lists",
        "nav_settings": "Settings",
        # Login / Register
        "login_title": "Welcome",
        "login_subtitle_login": "Sign in to view your lists",
        "login_subtitle_register": "Create your account to get started",
        "username_hint": "Username",
        "password_hint": "Password",
        "login": "Sign in",
        "create_account": "Create account",
        "switch_to_register": "Create a new account",
        "switch_to_login": "I have an account · Sign in",
        "logout": "Sign out",
        "auth_empty": "Fill in username and password.",
        "auth_user_not_found": "User not found.",
        "auth_wrong_password": "Wrong password.",
        "auth_user_exists": "That username is taken.",
        # Lowest prices
        "lowest_prices": "Lowest prices",
        "lowest_prices_sub": "Price history by store",
        "no_prices": "No prices recorded",
        "no_prices_sub": "Prices are saved when adding items with price to a list with a store.",
        "lowest_price_label": "Lowest price",
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
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def format_price(value):
    digits = clean_price(value)
    if not digits:
        return ""
    return "$" + f"{int(digits):,}".replace(",", ".")


def _normalize_item_name(name):
    return (name or "").strip().lower()


# ─────────────────────────────────────────────────────────────────────────
#  Persistencia
# ─────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILENAME = "usuarios.json"
GLOBAL_PRICES_FILENAME = "precios_globales.json"
LIST_TYPES = ("checklist", "notepad")
KV_PATH = os.path.join(BASE_DIR, "interfaz.kv")

LEGACY_LIST_FILE = "listas.json"  # compatibilidad con versiones anteriores


def _hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()


def _safe_username(username):
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", username or "").strip("_")
    return safe or "anon"


def normalize_list(raw):
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
                        "price": clean_price(it.get("price", "")),
                        "done": bool(it.get("done", False)),
                        "done_at": str(it.get("done_at") or ""),
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


def register_fonts():
    regular = os.path.join(BASE_DIR, "fonts", "Inter-Regular.ttf")
    bold = os.path.join(BASE_DIR, "fonts", "Inter-Bold.ttf")
    if os.path.exists(regular) and os.path.exists(bold):
        LabelBase.register(name="Inter", fn_regular=regular, fn_bold=bold)
        return "Inter"
    return "Roboto"


# ─────────────────────────────────────────────────────────────────────────
#  Widgets reutilizables
# ─────────────────────────────────────────────────────────────────────────
class Pressable(ButtonBehavior):
    """Botón base que registra automáticamente cada pulsación."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self._register_metric_press)

    def _register_metric_press(self, *_):
        app = MDApp.get_running_app()
        if app is not None and hasattr(app, "register_button_press"):
            app.register_button_press(self)


class BaseTxt(Label):
    pass


class Txt(BaseTxt):
    pass


class TxtAuto(BaseTxt):
    pass


class Card(BoxLayout):
    fill_color = ColorProperty([0, 0, 0, 0])
    border_color = ColorProperty([0, 0, 0, 0])
    radius = NumericProperty(dp(20))


class TapCard(Pressable, Card):
    pass


class PillButton(Pressable, AnchorLayout):
    text = StringProperty()
    icon = StringProperty("plus")


class FormButton(Pressable, AnchorLayout):
    text = StringProperty()
    icon = StringProperty("check")


class AddButton(Pressable, AnchorLayout):
    icon = StringProperty("plus")


class LinkButton(Pressable, AnchorLayout):
    text = StringProperty()
    tint = ColorProperty([1, 1, 1, 1])


class IconButton(Pressable, AnchorLayout):
    icon = StringProperty("arrow-left")


class DeleteButton(Pressable, AnchorLayout):
    pass


class NavItem(Pressable, AnchorLayout):
    key = StringProperty()
    icon = StringProperty()
    text = StringProperty()
    active = BooleanProperty(False)


class SettingRow(TapCard):
    icon = StringProperty()
    text = StringProperty()


class CheckMark(Widget):
    active = BooleanProperty(False)


class SoftProgress(Widget):
    value = NumericProperty(0)


class ToggleSwitch(Pressable, Widget):
    active = BooleanProperty(True)
    progress = NumericProperty(1)

    def on_release(self):
        self.active = not self.active
        Animation(progress=1 if self.active else 0, duration=0.15).start(self)


class FieldBase(Card):
    text = StringProperty()
    hint = StringProperty()
    error = BooleanProperty(False)

    __events__ = ("on_submit",)

    def on_submit(self):
        pass


class InputField(FieldBase):
    icon = StringProperty("format-list-bulleted")


class QuickInput(FieldBase):
    numeric = BooleanProperty(False)


class TypeOption(Pressable, Card):
    key = StringProperty()
    icon = StringProperty()
    title = StringProperty()
    desc = StringProperty()
    selected = BooleanProperty(False)


class ListCard(TapCard):
    list_id = StringProperty()
    name = StringProperty()
    subtitle = StringProperty()
    meta = StringProperty()
    icon = StringProperty("basket-outline")


class EmptyState(BoxLayout):
    pass


# ── Widgets para la pantalla "Precios más bajos" ─────────────────────────
class PriceItemSection(Card):
    item_name = StringProperty()


class PriceStoreRow(BoxLayout):
    store = StringProperty()
    price = StringProperty()
    item_key = StringProperty()
    is_lowest = BooleanProperty(False)


class EmptyPrices(BoxLayout):
    pass


class ShoppingItem(Pressable, Card):
    title = StringProperty()
    price = StringProperty()
    price_text = StringProperty()
    cheaper_text = StringProperty("")
    done = BooleanProperty(False)
    title_markup = StringProperty()
    item = ObjectProperty(None, allownone=True)

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
            self.item["done_at"] = datetime.now().isoformat(timespec="seconds") if self.done else ""
        app = MDApp.get_running_app()
        if app is not None:
            app.items_changed()
            self._refresh_cheaper_hint(app)

    def _refresh_cheaper_hint(self, app):
        if self.done or self.item is None:
            self.cheaper_text = ""
            return
        lst = app.current_list()
        if lst is None:
            self.cheaper_text = ""
            return
        price = int(clean_price(self.price) or 0)
        self.cheaper_text = app._cheaper_text(self.title, price, lst["store"])

    def _sync_title(self):
        text = escape_markup(self.title)
        self.title_markup = f"[s]{text}[/s]" if self.done else text


class LangOption(Pressable, BoxLayout):
    code = StringProperty()
    label = StringProperty()
    selected = BooleanProperty(False)


class LanguageDropDown(DropDown):
    def _reposition(self, *args):
        super()._reposition(*args)
        if self.attach_to is None:
            return
        right_edge = self.attach_to.to_window(self.attach_to.right, 0)[0]
        self.x = max(right_edge - self.width, 0)

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
    current_tab = StringProperty("inicio")
    lang = StringProperty("es")
    theme_dark = BooleanProperty(True)

    lists_count = NumericProperty(0)

    # Resumen de Analytics
    analytics_month_spend = StringProperty("$0")
    analytics_completed = StringProperty("0")
    analytics_top_product = StringProperty("Sin datos")
    analytics_top_store = StringProperty("Sin datos")
    analytics_estimated_savings = StringProperty("$0")
    analytics_summary = StringProperty("Agrega y marca productos como comprados para generar estadísticas.")

    detail_name = StringProperty("")
    detail_meta = StringProperty("")
    detail_kind = StringProperty("checklist")
    detail_notes = StringProperty("")
    total_items = NumericProperty(0)
    done_items = NumericProperty(0)
    progress = NumericProperty(0)
    percent = NumericProperty(0)
    total_text = StringProperty("$0")
    new_item_name = StringProperty("")
    new_item_price = StringProperty("")

    form_mode = StringProperty("new")
    form_name = StringProperty("")
    form_store = StringProperty("")
    form_type = StringProperty("checklist")
    delete_armed = BooleanProperty(False)
    prices_clear_armed = BooleanProperty(False)

    # Autenticación
    auth_username = StringProperty("")
    auth_password = StringProperty("")
    auth_error = StringProperty("")
    auth_mode = StringProperty("login")   # "login" o "register"
    current_user = StringProperty("")
    has_users = BooleanProperty(False)

    # Tema
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

    SCREEN_ORDER = ("inicio", "listas", "resumen", "detalle", "ajustes", "precios")

    # ── Ciclo de vida ───────────────────────────────────────────────────
    def build(self):
        self.title = "Lista de compras"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Lime"
        self.font_name = register_fonts()
        Window.clearcolor = self.bg_color
        Window.bind(on_keyboard=self._on_keyboard)
        Window.bind(on_resize=lambda *_: self._schedule_ui_check())

        self.users_file = self._users_path()
        self.prices_file = os.path.join(self._data_dir(), GLOBAL_PRICES_FILENAME)
        self.global_prices = self.load_global_prices()
        self._prices_disarm_event = None

        _users = self.load_users()
        _accounts = _users.get("users", {}) if isinstance(_users, dict) else {}
        self.has_users = bool(_accounts)
        saved = _users.get("current_user", "") if isinstance(_users, dict) else ""

        self.data_file = None
        self.lists = []
        self.current_id = None
        self._form_origin = "listas"
        self._disarm_event = None

        # Métricas de uso en un informe de texto fácil de leer.
        self.metrics_file = os.path.join(self._data_dir(), "metricas.txt")
        self.metrics = self.load_metrics()
        self.metrics["sessions"] = int(self.metrics.get("sessions", 0)) + 1
        self.metrics["last_session"] = datetime.now().isoformat(timespec="seconds")
        self._screen_started_at = time.monotonic()
        self._active_metric_screen = None

        if saved and saved in _accounts:
            self.current_user = saved
            self._load_user_data(migrate_legacy=True)
            self.auth_mode = "login"
        else:
            self.current_user = ""
            self.auth_mode = "login" if self.has_users else "register"

        root = Builder.load_file(KV_PATH)
        self.items_scroll = Factory.ItemsScroll()
        self.notes_card = Factory.NotesCard()
        root.ids.sm.current = "inicio" if self.current_user else "login"
        self._start_screen_metrics(root.ids.sm.current)
        self.save_metrics()
        return root

    def on_start(self):
        sm = self.root.ids.sm
        sm.transition = SlideTransition(duration=0.2)
        if self.current_user:
            self.refresh_lists()

    def on_pause(self):
        self.save_now()
        self._finish_screen_metrics()
        self.save_metrics()
        return True

    def on_resume(self):
        if self.current_user:
            self.refresh_lists()
            self.ui_check()
        if self._active_metric_screen:
            self._screen_started_at = time.monotonic()

    def on_stop(self):
        self.save_now()
        self._finish_screen_metrics()
        self.save_metrics()

    # ── Métricas de uso ─────────────────────────────────────────────────
    def load_metrics(self):
        """Recupera las métricas desde un TXT con formato legible."""
        data = {
            "version": 1, "sessions": 0, "buttons": {}, "screens": {},
            "navigation": {}, "events": [],
        }
        try:
            with open(self.metrics_file, "r", encoding="utf-8") as file:
                section = None
                for raw_line in file:
                    line = raw_line.strip()
                    if line.startswith("Sesiones iniciadas:"):
                        try: data["sessions"] = int(line.split(":", 1)[1].strip())
                        except ValueError: pass
                    elif line.startswith("Última sesión:"):
                        data["last_session"] = line.split(":", 1)[1].strip()
                    elif line == "DETALLE DE PANTALLAS": section = "screens"
                    elif line == "PULSACIONES DE BOTONES": section = "buttons"
                    elif line in ("RESUMEN DE USO", "================================", "--------------------", "----------------------", ""):
                        continue
                    elif section == "screens" and line.startswith("- ") and "|" in line:
                        name, details = line[2:].split("|", 1)
                        if "[" in name and name.endswith("]"):
                            name = name.rsplit("[", 1)[1][:-1]
                        values = {}
                        for part in details.split(";"):
                            if "=" in part:
                                k, v = part.split("=", 1)
                                values[k.strip()] = v.strip()
                        try:
                            data["screens"][name.strip()] = {
                                "visits": int(values.get("visitas", "0")),
                                "total_time_seconds": float(values.get("tiempo_segundos", "0")),
                            }
                        except ValueError: pass
                    elif section == "buttons" and line.startswith("- ") and "|" in line:
                        name, count = line[2:].rsplit("|", 1)
                        try: data["buttons"][name.strip()] = int(count.strip().split()[0])
                        except (ValueError, IndexError): pass
        except FileNotFoundError:
            # Migra las métricas de la versión anterior (JSON) al nuevo TXT.
            legacy_path = os.path.join(self._data_dir(), "metricas.json")
            try:
                with open(legacy_path, "r", encoding="utf-8") as file:
                    legacy = json.load(file)
                if isinstance(legacy, dict):
                    for key in ("sessions", "last_session", "buttons", "screens", "navigation", "events"):
                        if key in legacy:
                            data[key] = legacy[key]
            except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeDecodeError):
                pass
        except (OSError, UnicodeDecodeError):
            pass
        return data

    @staticmethod
    def _format_metric_time(seconds):
        seconds = max(0, int(seconds))
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        parts = []
        if hours: parts.append(f"{hours} h")
        if minutes: parts.append(f"{minutes} min")
        if secs or not parts: parts.append(f"{secs} s")
        return " ".join(parts)

    def save_metrics(self):
        """Guarda las estadísticas como un informe TXT comprensible."""
        if not getattr(self, "metrics_file", None):
            return
        try:
            lines = [
                "RESUMEN DE USO DE LA APLICACIÓN",
                "================================",
                f"Sesiones iniciadas: {self.metrics.get('sessions', 0)}",
                f"Última sesión: {self.metrics.get('last_session', 'Sin registros')}",
                "",
                "DETALLE DE PANTALLAS",
                "--------------------",
            ]
            screens = self.metrics.get("screens", {})
            if screens:
                screen_names = {
                    "inicio": "Inicio", "listas": "Mis listas", "resumen": "Resumen",
                    "detalle": "Detalle de lista", "nueva": "Nueva lista",
                    "ajustes": "Ajustes", "login": "Inicio de sesión",
                    "precios": "Precios más bajos",
                }
                for name, record in sorted(screens.items()):
                    visits = int(record.get("visits", 0))
                    seconds = float(record.get("total_time_seconds", 0))
                    readable_name = screen_names.get(name, name.replace("_", " ").capitalize())
                    lines.append(f"- {readable_name} [{name}] | visitas={visits}; tiempo={self._format_metric_time(seconds)}; tiempo_segundos={seconds:.2f}")
            else:
                lines.append("Todavía no hay visitas registradas.")
            lines.extend(["", "PULSACIONES DE BOTONES", "----------------------"])
            buttons = self.metrics.get("buttons", {})
            if buttons:
                for name, count in sorted(buttons.items(), key=lambda item: (-item[1], item[0])):
                    lines.append(f"- {name} | {count} pulsaciones")
            else:
                lines.append("Todavía no hay pulsaciones registradas.")
            lines.extend(["", "Nota: el tiempo se acumula mientras la aplicación permanece en cada pantalla."])
            tmp_path = self.metrics_file + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as file:
                file.write("\n".join(lines) + "\n")
            os.replace(tmp_path, self.metrics_file)
        except OSError as exc:
            Logger.error(f"Métricas: no se pudo guardar {self.metrics_file}: {exc}")

    def _start_screen_metrics(self, screen_name):
        self._active_metric_screen = screen_name
        self._screen_started_at = time.monotonic()
        record = self.metrics.setdefault("screens", {}).setdefault(
            screen_name, {"visits": 0, "total_time_seconds": 0.0}
        )
        record["visits"] = int(record.get("visits", 0)) + 1
        self.metrics.setdefault("events", []).append({
            "type": "screen_open",
            "screen": screen_name,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        })
        self._trim_metric_events()

    def _finish_screen_metrics(self):
        screen_name = getattr(self, "_active_metric_screen", None)
        started = getattr(self, "_screen_started_at", None)
        if not screen_name or started is None:
            return
        elapsed = max(0.0, time.monotonic() - started)
        record = self.metrics.setdefault("screens", {}).setdefault(
            screen_name, {"visits": 0, "total_time_seconds": 0.0}
        )
        record["total_time_seconds"] = round(
            float(record.get("total_time_seconds", 0.0)) + elapsed, 2
        )
        self.metrics["last_screen"] = screen_name
        self.metrics["last_screen_duration_seconds"] = round(elapsed, 2)
        # Reinicia el contador para que llamadas repetidas (pausa/cierre) no
        # contabilicen dos veces el mismo intervalo.
        self._screen_started_at = time.monotonic()

    def _trim_metric_events(self):
        # Evita que el historial de eventos crezca indefinidamente.
        events = self.metrics.setdefault("events", [])
        if len(events) > 1000:
            del events[:-1000]

    def register_button_press(self, widget):
        """Registra las pulsaciones de los widgets basados en Pressable."""
        label = ""
        for attr in ("text", "key", "name", "title", "icon"):
            value = getattr(widget, attr, "")
            if value:
                label = str(value).strip()
                if label:
                    break
        if not label:
            label = widget.__class__.__name__
        button_key = f"{widget.__class__.__name__}:{label}"
        buttons = self.metrics.setdefault("buttons", {})
        buttons[button_key] = int(buttons.get(button_key, 0)) + 1
        self.metrics.setdefault("events", []).append({
            "type": "button_press",
            "button": button_key,
            "screen": self.root.ids.sm.current if self.root else "unknown",
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        })
        self._trim_metric_events()
        self.save_metrics()

    # ── Persistencia: listas ────────────────────────────────────────────
    def _data_dir(self):
        return self.user_data_dir if platform in ("android", "ios") else BASE_DIR

    def _data_path_for(self, username):
        """Archivo de listas propio de cada usuario."""
        return os.path.join(self._data_dir(), f"listas_{_safe_username(username)}.json")

    def _load_user_data(self, migrate_legacy=False):
        """Asocia self.data_file/self.lists a la cuenta actual."""
        self.data_file = self._data_path_for(self.current_user)

        if migrate_legacy:
            # Si existía el archivo antiguo (una sola lista global), se copia
            # al usuario recordado la primera vez que arranca esta versión.
            legacy = os.path.join(self._data_dir(), LEGACY_LIST_FILE)
            if not os.path.exists(self.data_file) and os.path.exists(legacy):
                try:
                    shutil.copy2(legacy, self.data_file)
                    Logger.info(f"Listas: migradas de {legacy} a {self.data_file}")
                except OSError as exc:
                    Logger.warning(f"Listas: no se pudo migrar: {exc}")

        self.lists = self.load_lists()
        self.current_id = None

    def load_lists(self):
        if not self.data_file:
            return []
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
            Logger.error(f"Listas: no se pudo leer {self.data_file}: {exc}")
            try:
                os.replace(self.data_file, self.data_file + ".dañado")
            except OSError:
                pass
            return []
        raw_lists = data.get("lists", []) if isinstance(data, dict) else []
        lists = [normalize_list(raw) for raw in raw_lists]
        return [lst for lst in lists if lst is not None]

    def save_now(self, *_):
        Clock.unschedule(self.save_now)
        if not self.data_file:
            return
        payload = {"version": 1, "lists": self.lists}
        tmp_path = self.data_file + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.data_file)
        except OSError as exc:
            Logger.error(f"Listas: no se pudo guardar {self.data_file}: {exc}")

    def schedule_save(self, delay=0.6):
        Clock.unschedule(self.save_now)
        Clock.schedule_once(self.save_now, delay)

    # ── Persistencia: usuarios ──────────────────────────────────────────
    def _users_path(self):
        return os.path.join(self._data_dir(), USERS_FILENAME)

    def load_users(self):
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except FileNotFoundError:
            return {}
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
            Logger.error(f"Usuarios: no se pudo leer {self.users_file}: {exc}")
            return {}

    def save_users(self, data):
        tmp_path = self.users_file + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.users_file)
        except OSError as exc:
            Logger.error(f"Usuarios: no se pudo guardar {self.users_file}: {exc}")

    # ── Persistencia: precios globales por comercio ─────────────────────
    def load_global_prices(self):
        try:
            with open(self.prices_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return {}
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
            Logger.error(f"Precios: no se pudo leer {self.prices_file}: {exc}")
            return {}

        items = data.get("items", {}) if isinstance(data, dict) else {}
        cleaned = {}
        for key, stores in items.items():
            if not isinstance(stores, dict):
                continue
            bucket = {}
            for store, price in stores.items():
                store = str(store).strip()
                try:
                    value = int(price)
                except (TypeError, ValueError):
                    continue
                if store and value > 0:
                    bucket[store] = value
            if bucket:
                cleaned[str(key).strip().lower()] = bucket
        return cleaned

    def save_global_prices(self):
        if not self.prices_file:
            return
        tmp = self.prices_file + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"version": 1, "items": self.global_prices}, f,
                          ensure_ascii=False, indent=2)
            os.replace(tmp, self.prices_file)
        except OSError as exc:
            Logger.error(f"Precios: no se pudo guardar {self.prices_file}: {exc}")

    def _record_price(self, name, store, price):
        """Guarda `price` como el precio del artículo `name` en `store` y
        devuelve (comercio_más_barato, precio) si OTRO comercio lo tiene más
        barato; si no, devuelve None."""
        key = _normalize_item_name(name)
        if not key or not store or price <= 0:
            return None

        bucket = self.global_prices.setdefault(key, {})
        cheaper = None
        for other_store, other_price in bucket.items():
            if other_store == store:
                continue
            if other_price < price and (cheaper is None or other_price < cheaper[1]):
                cheaper = (other_store, other_price)

        bucket[store] = price
        self.save_global_prices()
        return cheaper

    def _cheaper_for(self, item_name, current_price, current_store):
        """Devuelve (comercio, precio) del comercio más barato (distinto al
        actual) para `item_name`, o None si no hay uno más barato."""
        if not current_store:
            return None
        key = _normalize_item_name(item_name)
        if not key or current_price <= 0:
            return None
        known = self.global_prices.get(key, {})
        cheaper = None
        for store, price in known.items():
            if store == current_store:
                continue
            try:
                value = int(price)
            except (TypeError, ValueError):
                continue
            if value > 0 and value < current_price:
                if cheaper is None or value < cheaper[1]:
                    cheaper = (store, value)
        return cheaper

    def _cheaper_text(self, item_name, current_price, current_store):
        cheaper = self._cheaper_for(item_name, current_price, current_store)
        if cheaper is None:
            return ""
        store, price = cheaper
        if self.lang == "en":
            return f"Cheaper at {store}: {format_price(price)}"
        return f"Más barato en {store}: {format_price(price)}"

    def _list_savings(self, lst):
        """Ahorro potencial sumando, por artículo pendiente, la diferencia con
        el comercio más barato conocido. Devuelve 0 si no hay ahorro."""
        total = 0
        for it in lst["items"]:
            if it["done"]:
                continue
            price = int(clean_price(it["price"]) or 0)
            if price <= 0:
                continue
            cheaper = self._cheaper_for(it["title"], price, lst["store"])
            if cheaper is not None:
                total += price - cheaper[1]
        return total

    def clear_global_prices(self):
        self.global_prices = {}
        try:
            if os.path.exists(self.prices_file):
                os.remove(self.prices_file)
            Logger.info("Precios: historial global borrado")
        except OSError as exc:
            Logger.error(f"Precios: no se pudo borrar {self.prices_file}: {exc}")

    def request_clear_prices(self):
        if not self.prices_clear_armed:
            self.prices_clear_armed = True
            self._prices_disarm_event = Clock.schedule_once(
                self._disarm_clear_prices, 3
            )
            return
        self._disarm_clear_prices()
        self.clear_global_prices()
        # Refresca la vista de precios si está en foco.
        if self.root is not None and self.root.ids.sm.current == "precios":
            self.refresh_lowest_prices()

    def _disarm_clear_prices(self, *_):
        if self._prices_disarm_event is not None:
            self._prices_disarm_event.cancel()
            self._prices_disarm_event = None
        self.prices_clear_armed = False

    # ── Pantalla "Precios más bajos" ────────────────────────────────────
    def open_lowest_prices(self):
        self.refresh_lowest_prices()
        self.go("precios")

    def refresh_lowest_prices(self):
        box = self.root.ids.sm.get_screen("precios").ids.prices_box
        box.clear_widgets()
        if not self.global_prices:
            box.add_widget(EmptyPrices())
            return
        for key in sorted(self.global_prices.keys()):
            stores = self.global_prices[key]
            if not stores:
                continue
            lowest_price = min(stores.values())
            section = PriceItemSection(item_name=key.capitalize())
            for store, price in sorted(stores.items(), key=lambda x: x[1]):
                section.add_widget(
                    PriceStoreRow(
                        store=store,
                        price=format_price(price),
                        item_key=key,
                        is_lowest=(price == lowest_price),
                    )
                )
            box.add_widget(section)

    def delete_price(self, item_key, store):
        bucket = self.global_prices.get(item_key)
        if bucket is None:
            return
        bucket.pop(store, None)
        if not bucket:
            del self.global_prices[item_key]
        self.save_global_prices()
        self.refresh_lowest_prices()
        if self.current_user:
            self.refresh_lists()

    # ── Login / Registro ────────────────────────────────────────────────
    def toggle_auth_mode(self):
        self.auth_mode = "login" if self.auth_mode == "register" else "register"
        self.auth_error = ""

    def submit_auth(self):
        self.auth_error = ""
        username = self.auth_username.strip()
        password = self.auth_password

        if not username or not password:
            self.auth_error = self.tr(self.lang, "auth_empty")
            return

        data = self.load_users()
        accounts = data.get("users", {})
        if not isinstance(accounts, dict):
            accounts = {}

        if self.auth_mode == "register":
            if username in accounts:
                self.auth_error = self.tr(self.lang, "auth_user_exists")
                return
            salt = secrets.token_hex(16)
            accounts[username] = {
                "salt": salt,
                "hash": _hash_password(password, salt),
            }
            data["users"] = accounts
            data["current_user"] = username
            self.save_users(data)
            self.has_users = True
            self.current_user = username
            self._load_user_data()
            self._enter_app()
            return

        # Login
        record = accounts.get(username)
        if record is None:
            self.auth_error = self.tr(self.lang, "auth_user_not_found")
            return
        if _hash_password(password, record.get("salt", "")) != record.get("hash", ""):
            self.auth_error = self.tr(self.lang, "auth_wrong_password")
            return

        data["current_user"] = username
        self.save_users(data)
        self.current_user = username
        self._load_user_data()
        self._enter_app()

    def _enter_app(self):
        self.auth_password = ""
        self.auth_error = ""
        self.refresh_lists()
        self.go("inicio")

    def do_logout(self):
        data = self.load_users()
        data.pop("current_user", None)
        self.save_users(data)
        self.current_user = ""
        self.data_file = None
        self.lists = []
        self.current_id = None
        self.auth_username = ""
        self.auth_password = ""
        self.auth_error = ""
        self.auth_mode = "login"
        self.go("login")

    def test_notification(self):
        notify_test(self.lang)

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
        self._finish_screen_metrics()
        Window.release_all_keyboards()
        if screen_name == "nueva":
            direction = "up"
        elif sm.current == "nueva":
            direction = "down"
        elif sm.current == "login" or screen_name == "login":
            direction = "up"
        else:
            order = self.SCREEN_ORDER
            forward = order.index(screen_name) > order.index(sm.current)
            direction = "left" if forward else "right"
        sm.transition.direction = direction
        sm.current = screen_name
        self._start_screen_metrics(screen_name)
        self.save_metrics()
        self._schedule_ui_check()
        if screen_name in ("detalle", "nueva"):
            self.current_tab = "listas"
        elif screen_name in ("inicio", "listas", "resumen", "ajustes"):
            self.current_tab = screen_name
        elif screen_name == "precios":
            self.current_tab = "ajustes"
        if screen_name == "resumen":
            self.refresh_analytics()

    def _on_keyboard(self, _window, key, *_args):
        if key != 27:
            return False
        current = self.root.ids.sm.current
        if current == "login":
            return False
        if current == "nueva":
            self.cancel_form()
            return True
        if current == "detalle":
            self.go("listas")
            return True
        if current == "precios":
            self.go("ajustes")
            return True
        return False

    # ── Formulario crear / editar ───────────────────────────────────────
    def open_form_new(self):
        self.form_mode = "new"
        self.form_name = ""
        self.form_store = ""
        self.form_type = "checklist"
        self._open_form()

    def open_form_edit(self):
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
        # Siempre mostramos la fecha concreta (no "hoy") para que el usuario
        # pueda identificar de un vistazo cuándo se actualizó cada lista.
        when = self.tr(self.lang, "updated_on").format(
            format_date(lst["updated"], self.lang, weekday=False)
        )
        base = f"{lst['store']} · {when}" if lst["store"] else when
        savings = self._list_savings(lst)
        if savings > 0:
            if self.lang == "en":
                base = f"{base} · save up to {format_price(savings)}"
            else:
                base = f"{base} · ahorras hasta {format_price(savings)}"
        return base

    def refresh_lists(self):
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
            price_val = int(clean_price(it["price"]) or 0)
            cheaper_text = ""
            if not it["done"] and price_val > 0:
                cheaper_text = self._cheaper_text(it["title"], price_val, lst["store"])
            box.add_widget(
                ShoppingItem(
                    title=it["title"], price=it["price"], done=it["done"],
                    cheaper_text=cheaper_text, item=it,
                )
            )
        self._show_body(lst["type"])
        scroll.scroll_y = 1
        self.refresh_progress()
        if check:
            self._schedule_ui_check()

    def add_item(self):
        lst = self.current_list()
        name = self.new_item_name.strip()
        if lst is None or not name:
            return

        price = clean_price(self.new_item_price)
        store = (lst["store"] or "").strip()

        item = {"title": name, "price": price, "done": False}
        lst["items"].append(item)

        cheaper_text = ""
        if price and store:
            price_value = int(price)
            cheaper = self._record_price(name, store, price_value)
            if cheaper is not None:
                cheaper_store, cheaper_price = cheaper
                if self.lang == "en":
                    cheaper_text = f"Cheaper at {cheaper_store}: {format_price(cheaper_price)}"
                else:
                    cheaper_text = f"Más barato en {cheaper_store}: {format_price(cheaper_price)}"
                notify_cheaper_store(
                    name, store, price_value,
                    cheaper_store, cheaper_price, self.lang,
                )

        self._items_widgets()[1].add_widget(
            ShoppingItem(
                title=item["title"], price=item["price"],
                cheaper_text=cheaper_text, item=item,
            )
        )
        self.new_item_name = ""
        self.new_item_price = ""
        self.items_changed()
        Clock.schedule_once(self._scroll_items_to_end, 0.05)

    def _items_widgets(self):
        return self.items_scroll, self.items_scroll.ids.item_list

    def _show_body(self, kind):
        body = self.root.ids.sm.get_screen("detalle").ids.body
        wanted = self.items_scroll if kind == "checklist" else self.notes_card
        unwanted = self.notes_card if kind == "checklist" else self.items_scroll
        if unwanted in body.children:
            body.remove_widget(unwanted)
        if wanted not in body.children:
            body.add_widget(wanted)

    def _scroll_items_to_end(self, *_):
        scroll, box = self._items_widgets()
        if box.minimum_height > scroll.height:
            scroll.scroll_y = 0

    # ── Autorreparación de la interfaz ──────────────────────────────────
    def _schedule_ui_check(self, *_):
        if self.root is None or "sm" not in self.root.ids:
            return
        Clock.unschedule(self.ui_check)
        Clock.schedule_once(self.ui_check, self.root.ids.sm.transition.duration + 0.35)

    @staticmethod
    def _hit_path(widget, x, y):
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
        if self.root is None or "sm" not in self.root.ids:
            return
        sm = self.root.ids.sm
        found = []
        if sm.transition.is_active:
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
            for button in (w for w in detail.walk() if isinstance(w, IconButton)):
                x, y = button.to_window(*button.center)
                path = self._hit_path(self.root, x, y)
                if path and button not in path:
                    found.append(
                        f"un toque sobre el botón '{button.icon}' lo recibe "
                        f"{self._describe(path[-1])}"
                    )
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
        lst = self.current_list()
        if lst is not None:
            self._touch(lst)
        self.refresh_progress()
        self.save_now()
        self.refresh_lists()

    def set_notes(self, text):
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
        self.total_text = format_price(
            sum(int(clean_price(it["price"]) or 0) for it in items)
        ) or "$0"
        self.progress = done / total if total else 0
        self.percent = int(round(self.progress * 100))

    # ── Analytics ───────────────────────────────────────────────────────
    def refresh_analytics(self):
        """Calcula indicadores a partir de los artículos marcados como comprados."""
        month_key = date.today().strftime("%Y-%m")
        completed = []
        month_spend = 0
        product_counts = {}
        store_counts = {}
        estimated_savings = 0

        for lst in self.lists:
            store = (lst.get("store") or "").strip() or "Sin comercio"
            for item in lst.get("items", []):
                if not item.get("done"):
                    continue
                completed.append(item)
                name = str(item.get("title") or "Producto").strip()
                key = _normalize_item_name(name)
                product_counts[name] = product_counts.get(name, 0) + 1
                store_counts[store] = store_counts.get(store, 0) + 1
                try:
                    price = int(clean_price(item.get("price", "")) or 0)
                except ValueError:
                    price = 0
                done_at = str(item.get("done_at") or "")
                if done_at[:7] == month_key:
                    month_spend += price
                # Ahorro potencial: diferencia frente al precio más bajo conocido
                # en otro comercio. No representa un ahorro ya realizado.
                known = self.global_prices.get(key, {})
                other_prices = [int(v) for k, v in known.items() if k != store and int(v) > 0]
                if price > 0 and other_prices and min(other_prices) < price:
                    estimated_savings += price - min(other_prices)

        self.analytics_month_spend = format_price(month_spend) or "$0"
        self.analytics_completed = str(len(completed))
        self.analytics_top_product = max(product_counts, key=product_counts.get) if product_counts else "Sin datos"
        self.analytics_top_store = max(store_counts, key=store_counts.get) if store_counts else "Sin datos"
        self.analytics_estimated_savings = format_price(estimated_savings) or "$0"
        legacy = sum(1 for lst in self.lists for it in lst.get("items", []) if it.get("done") and not it.get("done_at"))
        if not completed:
            self.analytics_summary = "Aún no hay artículos marcados como comprados."
        elif legacy:
            self.analytics_summary = f"{legacy} compra(s) antigua(s) no tienen fecha; el gasto mensual considera solo compras fechadas."
        else:
            self.analytics_summary = "Gastos del mes calculados con la fecha en que marcaste cada artículo como comprado."

    def get_monthly_expenses(self):
        """Devuelve el gasto de cada mes usando compras con fecha registrada."""
        totals = {}
        for lst in self.lists:
            for item in lst.get("items", []):
                stamp = str(item.get("done_at") or "")
                if item.get("done") and len(stamp) >= 7:
                    month = stamp[:7]
                    totals[month] = totals.get(month, 0) + int(clean_price(item.get("price", "")) or 0)
        return dict(sorted(totals.items()))

    def get_frequent_products(self, limit=5):
        """Entrega los productos más comprados y su cantidad."""
        counts = {}
        for lst in self.lists:
            for item in lst.get("items", []):
                if item.get("done"):
                    name = str(item.get("title") or "").strip()
                    if name:
                        counts[name] = counts.get(name, 0) + 1
        return sorted(counts.items(), key=lambda pair: pair[1], reverse=True)[:limit]

    def get_frequent_stores(self, limit=5):
        """Entrega los comercios con más artículos comprados en sus listas."""
        counts = {}
        for lst in self.lists:
            store = (lst.get("store") or "").strip()
            if store:
                count = sum(1 for item in lst.get("items", []) if item.get("done"))
                if count:
                    counts[store] = counts.get(store, 0) + count
        return sorted(counts.items(), key=lambda pair: pair[1], reverse=True)[:limit]

    # ── Tema ────────────────────────────────────────────────────────────
    def set_dark_mode(self, active):
        if active == self.theme_dark:
            return
        self.theme_dark = active
        self.theme_cls.theme_style = "Dark" if active else "Light"
        palette = PALETTE_DARK if active else PALETTE_LIGHT
        order = ["TEXT"] + [name for name in palette if name != "TEXT"]
        targets = {
            f"{name.lower()}_color": get_color_from_hex(palette[name])
            for name in order
        }
        Animation.cancel_all(self, *targets.keys())
        Animation(duration=0.35, t="out_quad", **targets).start(self)

    def on_bg_color(self, _instance, value):
        Window.clearcolor = value

    # ── Idioma ───────────────────────────────────────────────────────────
    def tr(self, lang, key):
        return TRANSLATIONS.get(lang, TRANSLATIONS["es"]).get(key, key)

    def set_language(self, code):
        if code in TRANSLATIONS:
            self.lang = code

    def on_lang(self, *_):
        if self.root is None:
            return
        self.refresh_lists()
        lst = self.current_list()
        if lst is not None:
            self._refresh_detail_meta(lst)
            # Recalcula los avisos de "más barato en..." con el idioma nuevo,
            # conservando scroll y lo que el usuario estuviera escribiendo.
            if (self.root.ids.sm.current == "detalle"
                    and lst["type"] == "checklist"
                    and not self.new_item_name and not self.new_item_price):
                scroll, _box = self._items_widgets()
                saved = scroll.scroll_y
                self._load_detail(lst, check=False)
                scroll.scroll_y = saved
        if self.root.ids.sm.current == "precios":
            self.refresh_lowest_prices()

    def open_language_menu(self, anchor):
        LanguageDropDown().open(anchor)


if __name__ == "__main__":
    ShoppingListApp().run()