"""
Notificaciones · Lista de compras
=================================

Muestra una notificación local cuando, al agregar un artículo a una lista,
ese mismo artículo (por nombre) tiene un precio más bajo en otro comercio
según el historial global de precios.

La notificación se programa con un pequeño retraso (`delay`) para que la
ventana ya esté dibujada cuando aparezca el aviso.

Estrategia por capas (todas con logging):

  1. plyer.notification  (multi-plataforma; el camino principal).
  2. Fallback nativo según la plataforma:
        Linux   → `notify-send`
        macOS   → `osascript`
        Windows → `winotify` (o `win10toast`)
  3. Si todo falla, se registra un warning.

Uso desde main.py:
    from noti import notify_cheaper_store, notify_test
    notify_cheaper_store("Leche", "Lider", 1500, "Jumbo", 1200, "es")

Instalación recomendada (según sistema):
    pip install plyer
    Windows:  pip install winotify      (o: pip install win10toast)
    Linux:    sudo apt install libnotify-bin
"""

import shutil
import subprocess

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform

APP_NAME = "Lista de compras"


# ─────────────────────────────────────────────────────────────────────
#  Mensajes
# ─────────────────────────────────────────────────────────────────────
def _format_price(value):
    return "$" + f"{int(value):,}".replace(",", ".")


def _build_cheaper_message(item_name, current_store, current_price,
                           cheaper_store, cheaper_price, lang):
    current_txt = _format_price(current_price)
    cheaper_txt = _format_price(cheaper_price)
    if lang == "en":
        title = "Better price found"
        body = (f'"{item_name}" is cheaper at {cheaper_store} '
                f'({cheaper_txt}) than at {current_store} ({current_txt}).')
    else:
        title = "Mejor precio encontrado"
        body = (f'"{item_name}" está más barato en {cheaper_store} '
                f'({cheaper_txt}) que en {current_store} ({current_txt}).')
    return title, body


# ─────────────────────────────────────────────────────────────────────
#  Backends
# ─────────────────────────────────────────────────────────────────────
def _try_plyer(title, body, timeout):
    try:
        from plyer import notification
    except ImportError:
        Logger.warning("Noti: 'plyer' no está instalado (pip install plyer)")
        return False
    try:
        notification.notify(
            title=title,
            message=body,
            app_name=APP_NAME,
            timeout=timeout,
        )
        Logger.info(f"Noti: mostrada vía plyer → {title} | {body}")
        return True
    except Exception as exc:
        Logger.warning(f"Noti: plyer falló: {exc}")
        return False


def _try_notify_send(title, body):
    if not shutil.which("notify-send"):
        Logger.warning("Noti: 'notify-send' no está instalado "
                       "(sudo apt install libnotify-bin)")
        return False
    try:
        subprocess.run(
            ["notify-send", "-a", APP_NAME, "-u", "normal", title, body],
            check=True, timeout=5,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        Logger.info(f"Noti: mostrada vía notify-send → {title}")
        return True
    except Exception as exc:
        Logger.warning(f"Noti: notify-send falló: {exc}")
        return False


def _try_osascript(title, body):
    safe_body = body.replace('"', "'")
    safe_title = title.replace('"', "'")
    script = f'display notification "{safe_body}" with title "{safe_title}"'
    try:
        subprocess.run(
            ["osascript", "-e", script],
            check=True, timeout=5,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        Logger.info(f"Noti: mostrada vía osascript → {title}")
        return True
    except Exception as exc:
        Logger.warning(f"Noti: osascript falló: {exc}")
        return False


def _try_winotify(title, body):
    try:
        from winotify import Notification
    except ImportError:
        Logger.warning("Noti: 'winotify' no está instalado "
                       "(pip install winotify)")
        return False
    try:
        toast = Notification(app_id=APP_NAME, title=title, msg=body, duration="short")
        toast.show()
        Logger.info(f"Noti: mostrada vía winotify → {title}")
        return True
    except Exception as exc:
        Logger.warning(f"Noti: winotify falló: {exc}")
        return False


def _try_win10toast(title, body):
    try:
        from win10toast import ToastNotifier
    except ImportError:
        return False
    try:
        ToastNotifier().show_toast(title, body, duration=8, threaded=True)
        Logger.info(f"Noti: mostrada vía win10toast → {title}")
        return True
    except Exception as exc:
        Logger.warning(f"Noti: win10toast falló: {exc}")
        return False


# ─────────────────────────────────────────────────────────────────────
#  Orquestación
# ─────────────────────────────────────────────────────────────────────
def _show(title, body, timeout):
    if _try_plyer(title, body, timeout):
        return True
    if platform == "linux" and _try_notify_send(title, body):
        return True
    if platform == "macosx" and _try_osascript(title, body):
        return True
    if platform == "win":
        if _try_winotify(title, body):
            return True
        if _try_win10toast(title, body):
            return True
    Logger.error("Noti: no se pudo mostrar la notificación por ningún medio")
    return False


def notify_cheaper_store(item_name, current_store, current_price,
                         cheaper_store, cheaper_price, lang="es",
                         timeout=10, delay=0.5):
    """Notifica que `item_name` está más barato en `cheaper_store`."""
    title, body = _build_cheaper_message(
        item_name, current_store, current_price,
        cheaper_store, cheaper_price, lang,
    )
    Clock.schedule_once(lambda dt: _show(title, body, timeout), delay)
    return True


def notify_test(lang="es"):
    """Dispara una notificación de prueba (usada por el botón de Ajustes)."""
    if lang == "en":
        return notify_cheaper_store("Milk", "Lider", 1500, "Jumbo", 1200,
                                    lang, delay=0.1)
    return notify_cheaper_store("Leche", "Lider", 1500, "Jumbo", 1200,
                                lang, delay=0.1)