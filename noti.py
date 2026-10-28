"""
Notificaciones · Lista de compras
=================================

Muestra una notificación local (nativa del sistema) cuando el usuario tiene
listas de compras pendientes. Usa `plyer`, que funciona en Android, iOS,
Windows, macOS y Linux con la misma API.

Instalación:
    pip install plyer

Uso desde main.py:
    from notificaciones import notify_pending_lists

    # …dentro de ShoppingListApp.on_start():
    notify_pending_lists(self.lists, self.lang)

En Android 13+ recuerda declarar el permiso en buildozer.spec:
    android.permissions = POST_NOTIFICATIONS
"""

from kivy.logger import Logger

try:
    from plyer import notification
    _PLYER_AVAILABLE = True
except ImportError:  # plyer no está instalado
    _PLYER_AVAILABLE = False


def notify_pending_lists(lists, lang="es", app_name="Lista de compras", timeout=10):
    """Muestra una notificación si hay listas pendientes.

    Parámetros
    ----------
    lists : list[dict]
        La lista de listas tal como la guarda ShoppingListApp (self.lists).
    lang : str
        "es" o "en"; se usa para elegir el idioma del texto.
    app_name : str
        Nombre que aparece en la notificación.
    timeout : int
        Segundos que permanece visible la notificación.

    Devuelve True si se pudo mostrar, False si no.
    """
    if not lists:
        return False

    if not _PLYER_AVAILABLE:
        Logger.warning(
            "Notificaciones: 'plyer' no está instalado, se omite el aviso. "
            "Instálalo con: pip install plyer"
        )
        return False

    if lang == "en":
        title = "Shopping list"
        message = f"You have {len(lists)} pending list(s)."
    else:
        title = "Lista de compras"
        message = f"Tienes {len(lists)} lista(s) pendiente(s)."

    try:
        notification.notify(
            title=title,
            message=message,
            app_name=app_name,
            timeout=timeout,
        )
        return True
    except Exception as exc:  # p. ej. falta permiso en Android 13+
        Logger.error(f"Notificaciones: no se pudo mostrar: {exc}")
        return False