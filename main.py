"""
Lista de compras · Kivy + KivyMD
=================================
(misma cabecera que antes)
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

# Soft keyboard: subir el contenido para que el campo enfocado quede por
# encima del teclado. `below_target` mueve la ventana lo necesario sin
# aplastar el layout (a diferencia de "resize" en Android).
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
        # Nuevos
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
        # New
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

LEGACY_LIST_FILE = "listas.json"


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
        self.price