[app]

# ═══════════════════════════════════════════════════════════════════════
#  Cyro Punch — Lista de compras (Kivy + KivyMD)
#  Generado para compilar la app Android con Buildozer / python-for-android
# ═══════════════════════════════════════════════════════════════════════

# Nombre visible de la aplicación
title = Cyro Punch

# Nombre del paquete: solo minúsculas, números, puntos o guiones bajos
package.name = cyropunch

# Dominio del paquete (organización inversa)
package.domain = org.cyropunch

# Directorio que contiene el código fuente
source.dir = .

# Extensiones de archivo que se incluirán en el APK
source.include_exts = py,kv,json,txt,md

# Directorios que NO se deben empaquetar
source.exclude_dirs = venv,bin,docs,build,.git,.github,.buildozer,__pycache__

# Versión de la aplicación
version = 1.0

# Dependencias para Android.
# NOTA: "winotify" de requirements.txt NO se incluye porque es exclusivo de
# Windows. En Android, noti.py usa "plyer" como vía principal de notificaciones.
# materialyoucolor / asynckivy / pillow son dependencias reales de KivyMD 2.0.0
# y deben listarse explícitamente para python-for-android.
requirements = python3,kivy==2.3.1,kivymd==2.0.0,materialyoucolor,asynckivy,pillow,plyer

# Orientación de la app (la UI está diseñada en formato teléfono vertical)
orientation = portrait

# La app maneja su propia navegación: no usar fullscreen
fullscreen = 0

# Permisos de Android
# - POST_NOTIFICATIONS: necesario en Android 13+ para las notificaciones
#   locales de "precio más barato en otro comercio" (noti.py vía plyer)
# - INTERNET no se requiere: la app funciona 100 % offline
android.permissions = POST_NOTIFICATIONS

# (Opcional) Ícono y pantalla de arranque — descomenta y ajusta la ruta:
# icon.filename = %(source.dir)s/assets/icon.png
# presplash.filename = %(source.dir)s/assets/presplash.png

# (Opcional) Firma para release. Genera el keystore con:
#   keytool -genkey -v -keystore cyropunch.keystore -alias cyropunch \
#           -keyalg RSA -keysize 2048 -validity 10000
# y descomenta:
# android.release_artifact = apk
# android.keystore_path = cyropunch.keystore
# android.keystore_pass = TU_PASSWORD
# android.keyalias = cyropunch
# android.keyalias_pass = TU_PASSWORD

[buildozer]

# Nivel de log: 1=info, 2=debug (útil si el build falla)
log_level = 2

# Advertir si buildozer se ejecuta como root
warn_on_root = 1
