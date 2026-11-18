"""
Notificaciones · Lista de compras
=================================

Muestra una notificación local cuando, al agregar un artículo a una lista,
ese mismo artículo (por nombre) tiene un precio más bajo en otro comercio
según el historial global de precios.

La notificación se programa con un pequeño retraso (`delay`) para que la
ventana ya esté dibujada cuando aparezca el aviso.

Estrategia por capas (todas con logging):

  0. En Android: backend nativo con pyjnius (androidx NotificationCompat).
  1. plyer.notification  (multi-plataforma; fallback en Android, principal
     en escritorio).
  2. Fallback nativo según plataforma de escritorio:
        Linux   → `notify-send`
        macOS   → `osascript`
        Windows → `winotify` (o `win10toast`)
  3. Si todo falla, se registra un warning.

Requisitos en buildozer.spec para el backend Android nativo:
    android.permissions = POST_NOTIFICATIONS
    android.enable_androidx = True
    android.gradle_dependencies = androidx.core:core:1.6.0
    requirements = ..., pyjnius, ...

Uso desde main.py:
    from noti import notify_cheaper_store, notify_test
    notify_cheaper_store("Leche", "Lider", 1500, "Jumbo", 1200, "es")
"""

import shutil
import subprocess

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform

APP_NAME = "Lista de compras"
ANDROID_CHANNEL_ID = "tmorganizer_channel"

# Contador para que cada notificación Android use un ID distinto y no se
# sobrescriba la anterior cuando llegan varias en poco tiempo.
_android_id_counter = [0]


def _next_android_id():
    _android_id_counter[0] += 1
    return _android_id_counter[0]


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
#  Backend Android nativo (pyjnius)
# ─────────────────────────────────────────────────────────────────────
def _try_android_native(title, body, timeout=10):
    """Notificación nativa con androidx.core.app.NotificationCompat.

    - Maneja el canal de notificación (obligatorio en Android 8+).
    - Pide POST_NOTIFICATIONS en Android 13+ (asíncrono, no bloquea).
    - Usa un icono del sistema para no depender de un drawable propio.
    """
    try:
        from jnius import autoclass
    except ImportError:
        Logger.warning("Noti: pyjnius no disponible")
        return False

    # Permiso POST_NOTIFICATIONS (Android 13+). Es asíncrono: si el usuario
    # todavía no ha concedido el permiso, esta primera notificación se pierde.
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.POST_NOTIFICATIONS])
    except Exception as exc:
        Logger.warning(f"Noti: no se pudo pedir POST_NOTIFICATIONS: {exc}")

    try:
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        NotificationManager = autoclass('android.app.NotificationManager')
        BuildVersion = autoclass('android.os.Build$VERSION')

        context = PythonActivity.mActivity
        manager = context.getSystemService(Context.NOTIFICATION_SERVICE)
        if manager is None:
            Logger.warning("Noti: NotificationManager no disponible")
            return False

        # Canal (Android 8+)
        if BuildVersion.SDK_INT >= 26:
            NotificationChannel = autoclass('android.app.NotificationChannel')
            channel = NotificationChannel(
                ANDROID_CHANNEL_ID,
                APP_NAME,
                NotificationManager.IMPORTANCE_HIGH,
            )
            manager.createNotificationChannel(channel)

        # Builder (androidx)
        BuilderClass = autoclass('androidx.core.app.NotificationCompat$Builder')
        builder = BuilderClass(context, ANDROID_CHANNEL_ID)
        builder.setContentTitle(title)
        builder.setContentText(body)
        builder.setAutoCancel(True)
        builder.setSmallIcon(autoclass('android.R$drawable').ic_dialog_info)
        try:
            NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
            builder.setPriority(NotificationCompat.PRIORITY_HIGH)
            builder.setDefaults(NotificationCompat.DEFAULT_ALL)
        except Exception:
            pass

        manager.notify(_next_android_id(), builder.build())
        Logger.info(f"Noti: Android nativo → {title} | {body}")
        return True
    except Exception as exc:
        Logger.warning(f"Noti: Android nativo falló: {exc}")
        return False


# ─────────────────────────────────────────────────────────────────────
#  Backend plyer (multi-plataforma)
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


# ─────────────────────────────────────────────────────────────────────
#  Backends de escritorio
# ─────────────────────────────────────────────────────────────────────
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
    # En Android probamos primero el backend nativo (más fiable).
    if platform == "android":
        if _try_android_native(title, body, timeout):
            return True
        if _try_plyer(title, body, timeout):
            return True
        Logger.error("Noti: Android - no se pudo mostrar la notificación")
        return False

    # Escritorio: plyer primero, luego fallbacks nativos por SO.
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