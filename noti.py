"""
Notificaciones · Lista de compras
=================================

Muestra una notificación local cuando, al agregar un artículo a una lista,
ese mismo artículo (por nombre) tiene un precio más bajo en otro comercio
según el historial global de precios.

La notificación se programa con un pequeño retraso (`delay`) para que la
ventana ya esté dibujada cuando aparezca el aviso.

Estrategia por capas (todas con logging):

  1. Android → API nativa vía pyjnius (canal de notificación + permiso
     POST_NOTIFICATIONS de Android 13+).
  2. plyer.notification  (multi-plataforma; también fallback en Android).
  3. Fallback nativo según la plataforma:
        Linux   → `notify-send`
        macOS   → `osascript`
        Windows → `winotify`
  4. Si todo falla, se registra un error.

Uso desde main.py:
    from noti import notify_cheaper_store, notify_test, request_notification_permission
    request_notification_permission()          # una vez, al arrancar
    notify_cheaper_store("Leche", "Lider", 1500, "Jumbo", 1200, "es")

Instalación recomendada (según sistema):
    pip install plyer
    Windows:  pip install winotify
    Linux:    sudo apt install libnotify-bin
    Android:  `pyjnius` y `plyer` en `requirements` + permiso POST_NOTIFICATIONS
              en buildozer.spec (android.permissions).
"""

import itertools
import shutil
import subprocess

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform

APP_NAME = "Lista de compras"
CHANNEL_ID = "price_alerts"
CHANNEL_NAME = "Alertas de precio"

_notification_ids = itertools.count(1)


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
#  Android (pyjnius)
# ─────────────────────────────────────────────────────────────────────
def request_notification_permission():
    """Pide POST_NOTIFICATIONS (Android 13+). En otras plataformas no hace nada.

    El permiso también debe declararse en buildozer.spec:
        android.permissions = POST_NOTIFICATIONS
    """
    if platform != "android":
        return
    try:
        from android.permissions import Permission, request_permissions
    except ImportError:
        Logger.warning("Noti: módulo 'android.permissions' no disponible")
        return
    permission = getattr(
        Permission, "POST_NOTIFICATIONS", "android.permission.POST_NOTIFICATIONS"
    )
    try:
        request_permissions([permission])
        Logger.info("Noti: permiso de notificaciones solicitado")
    except Exception as exc:
        Logger.warning(f"Noti: no se pudo pedir el permiso: {exc}")


def _try_android(title, body):
    try:
        from jnius import autoclass, cast
    except ImportError:
        Logger.warning("Noti: 'pyjnius' no está disponible")
        return False
    try:
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Context = autoclass("android.content.Context")
        BuildVersion = autoclass("android.os.Build$VERSION")
        NotificationManager = autoclass("android.app.NotificationManager")
        NotificationBuilder = autoclass("android.app.Notification$Builder")
        Intent = autoclass("android.content.Intent")
        PendingIntent = autoclass("android.app.PendingIntent")
        String = autoclass("java.lang.String")

        activity = PythonActivity.mActivity
        manager = activity.getSystemService(Context.NOTIFICATION_SERVICE)

        if BuildVersion.SDK_INT >= 26:
            NotificationChannel = autoclass("android.app.NotificationChannel")
            channel = NotificationChannel(
                String(CHANNEL_ID),
                cast("java.lang.CharSequence", String(CHANNEL_NAME)),
                NotificationManager.IMPORTANCE_DEFAULT,
            )
            manager.createNotificationChannel(channel)
            builder = NotificationBuilder(activity, String(CHANNEL_ID))
        else:
            builder = NotificationBuilder(activity)

        # Al tocar el aviso se vuelve a la app.
        intent = Intent(activity, PythonActivity)
        intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP
                        | Intent.FLAG_ACTIVITY_CLEAR_TOP)
        pending = PendingIntent.getActivity(
            activity, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE,
        )

        builder.setContentTitle(cast("java.lang.CharSequence", String(title)))
        builder.setContentText(cast("java.lang.CharSequence", String(body)))
        builder.setStyle(
            autoclass("android.app.Notification$BigTextStyle")().bigText(
                cast("java.lang.CharSequence", String(body))
            )
        )
        builder.setSmallIcon(activity.getApplicationInfo().icon)
        builder.setContentIntent(pending)
        builder.setAutoCancel(True)

        manager.notify(next(_notification_ids), builder.build())
        Logger.info(f"Noti: mostrada vía Android nativo → {title}")
        return True
    except Exception as exc:
        Logger.warning(f"Noti: Android nativo falló: {exc}")
        return False


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


def _applescript_quote(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _try_osascript(title, body):
    script = (f'display notification "{_applescript_quote(body)}" '
              f'with title "{_applescript_quote(title)}"')
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
        toast = Notification(app_id=APP_NAME, title=title, msg=body,
                             duration="short")
        toast.show()
        Logger.info(f"Noti: mostrada vía winotify → {title}")
        return True
    except Exception as exc:
        Logger.warning(f"Noti: winotify falló: {exc}")
        return False


# ─────────────────────────────────────────────────────────────────────
#  Orquestación
# ─────────────────────────────────────────────────────────────────────
def _show(title, body, timeout):
    if platform == "android" and _try_android(title, body):
        return True
    if _try_plyer(title, body, timeout):
        return True
    if platform == "linux" and _try_notify_send(title, body):
        return True
    if platform == "macosx" and _try_osascript(title, body):
        return True
    if platform == "win" and _try_winotify(title, body):
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
