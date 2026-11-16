[app]

# ── Identity ─────────────────────────────────────────────────────────────
title = Lista de compras
package.name = listacompras
package.domain = org.example

# ── Sources ──────────────────────────────────────────────────────────────
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf,otf,so
source.exclude_exts = spec,pyc,pyo,md,txt,log
source.exclude_dirs = tests, bin, venv, .git, .github, .buildozer, __pycache__, build, dists, .idea, .vscode
source.exclude_patterns = job-logs*,*.spec,*~

# ── Version ──────────────────────────────────────────────────────────────
version = 0.1

# ── Requirements  ← the critical part ───────────────────────────────────
# Kivy 2.3.1 is the last release that compiles cleanly on Python 3.10.
# KivyMD MUST be pinned to 1.1.1 – the 2.x branch pulls MaterialShapes
# (cairo) which has no p4a recipe and breaks the build.
# jnius>=1.4.0 is required for Python 3.10 compatibility.
# pillow and sdl2_ttf are runtime deps of KivyMD 1.1.1.
# plyer is used by noti.py.
requirements = python3,kivy==2.3.1,kivymd==1.1.1,pillow,plyer,sdl2_ttf==2.0.15,jnius>=1.4.0

# ── Splash / Icon (optional) ─────────────────────────────────────────────
# presplash.filename = %(source.dir)s/data/presplash.png
# presplash.color    = #0A0B0F
# icon.filename      = %(source.dir)s/data/icon.png

# ── Orientation ──────────────────────────────────────────────────────────
orientation = portrait
fullscreen  = 0

# ── Android SDK / NDK ────────────────────────────────────────────────────
# API 33 is more stable than 34 with the p4a toolchain on Ubuntu 22.04.
android.api     = 33
android.minapi  = 24
android.ndk     = 25b
android.ndk_api = 24
android.archs   = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

# POST_NOTIFICATIONS is required for Android 13+ notifications.
android.permissions = POST_NOTIFICATIONS,VIBRATE

# Keep user data in app-private storage.
android.private_storage = True
android.allow_backup    = True

# ── python-for-android ──────────────────────────────────────────────────
p4a.bootstrap = sdl2
# Leave p4a.branch at default (master); pinning it is not necessary.

# ── Logging ──────────────────────────────────────────────────────────────
log_level = 1