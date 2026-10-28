"""
Notificaciones · Lista de compras
=================================

Muestra una notificación local cuando el usuario tiene listas pendientes.

Estrategia por capas (todas con logging para que se vea en consola):

  1. plyer.notification  (multi-plataforma; el camino principal).
  2. Fallback nativo según la plataforma:
        Linux   → `notify-send`
        macOS   → `osascript`
        Windows → `winotify` (o `win10toast`)
        Android → plyer (necesita POST_NOTIFICATIONS en buildozer.spec)
  3. Si todo falla, se registra un warning.

La notificación se programa con un pequeño retraso (`delay`), para que la
ventana ya esté visible cuando aparezca el aviso. Llamarla desde on_start
sin retraso es la causa nº1 de "no se ve la notificación".

Uso desde main.py:
    from noti import notify_pending_lists
    notify_pending_lists(self.lists, self.lang)

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
def _build_message(lists, lang):
    """Devuelve (título, cuerpo) para la notificación."""
    n = len(lists)
    if lang == "en":
        title = "Shopping list"
        if n == 1:
            name = lists[0].get("name") or "your list"
            body = f'You have a pending list: "{name}".'
        else:
            body = f"You have {n} pending lists."
    else:
        title = "Lista de compras"
        if n == 1:
            name = lists[0].get("name") or "tu lista"
            body = f'Tienes una lista pendiente: "{name}".'
        else:
            body = f"Tienes {n} listas pendientes."
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
    """Fallback Linux: `notify-send` (paquete libnotify-bin)."""
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
    """Fallback macOS: `osascript` (Notification Center)."""
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
    """Fallback Windows: `winotify` (toast nativo de Win10/11)."""
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
    """Último recurso Windows: `win10toast`."""
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
def _show(lists, lang, timeout):
    if not lists:
        Logger.info("Noti: no hay listas pendientes, no se muestra nada")
        return False

    title, body = _build_message(lists, lang)

    # 1) plyer (Android / iOS / Linux / macOS / Windows)
    if _try_plyer(title, body, timeout):
        return True

    # 2) fallback según plataforma
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


def notify_pending_lists(lists, lang="es", timeout=10, delay=1.2):
    """Programa la notificación `delay` segundos después de la llamada.

    El retraso es importante: llamarla directamente en on_start a veces
    ocurre antes de que la ventana exista y algunos backends la descartan.
    Devuelve True si se programó (no garantiza que se muestre; eso lo
    decide `_show`, que además deja log).
    """
    if not lists:
        return False
    Clock.schedule_once(lambda dt: _show(lists, lang, timeout), delay)
    return True


def notify_test(lang="es"):
    """Dispara una notificación de prueba (usada por el botón de Ajustes)."""
    fake = [{"id": "test", "name": "Prueba" if lang == "es" else "Test"}]
    return notify_pending_lists(fake, lang, delay=0.1)