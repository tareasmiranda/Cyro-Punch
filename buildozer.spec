[app]

# ─────────────────────────────────────────────────────────────────────────
#  Identity
# ─────────────────────────────────────────────────────────────────────────
# (str) Title shown on the Android launcher
title = Lista de compras

# (str) Reverse-DNS package name. Must match package.domain + package.name
package.name = listacompras
package.domain = org.example

# ─────────────────────────────────────────────────────────────────────────
#  Sources
# ─────────────────────────────────────────────────────────────────────────
# (str) Folder that contains main.py (and noti.py, interfaz.kv, fonts/)
source.dir = .

# (list) Extensions of files to package inside the APK
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf,otf,so

# (list) Extensions to explicitly exclude
source.exclude_exts = spec,pyc,pyo,md,txt,log

# (list) Folders that must never be packaged
source.exclude_dirs = tests, bin, venv, .git, .github, .buildozer, __pycache__, build, dists, .idea, .vscode

# (list) Glob patterns to skip
source.exclude_patterns = job-logs*,*.spec,*~

# ─────────────────────────────────────────────────────────────────────────
#  Versioning
# ─────────────────────────────────────────────────────────────────────────
version = 0.1

# ─────────────────────────────────────────────────────────────────────────
#  Requirements  ← the most important part for a working build
# ─────────────────────────────────────────────────────────────────────────
# Kivy 2.3.1 is the last release that supports the Python 3.x toolchain
# shipped by p4a on Ubuntu 22.04.
# KivyMD MUST be pinned to 1.1.1: the 2.x branch pulls MaterialShapes which
# depends on pycairo — a package that has no python-for-android recipe and
# breaks every Android build.
# pillow and sdl2_ttf are direct runtime dependencies of KivyMD 1.1.1.
# plyer is used by noti.py for local notifications.
requirements = python3,kivy==2.3.1,kivymd==1.1.1,pillow,plyer,sdl2_ttf==2.0.15

# ─────────────────────────────────────────────────────────────────────────
#  Splash / Icon  (optional — uncomment once you add the files)
# ─────────────────────────────────────────────────────────────────────────
# presplash.filename = %(source.dir)s/data/presplash.png
# presplash.color    = #0A0B0F
# icon.filename      = %(source.dir)s/data/icon.png

# ─────────────────────────────────────────────────────────────────────────
#  Orientation / Fullscreen
# ─────────────────────────────────────────────────────────────────────────
orientation = portrait
fullscreen  = 0

# ─────────────────────────────────────────────────────────────────────────
#  Android manifest / SDK / NDK
# ─────────────────────────────────────────────────────────────────────────
# POST_NOTIFICATIONS is required on Android 13+ for noti.py to work.
# VIBRATE is harmless and lets the OS show the notification quietly.
android.permissions = POST_NOTIFICATIONS,VIBRATE

# Target / minimum API.  34 = Android 14, 24 = Android 7.0.
android.api     = 34
android.minapi  = 24

# NDK r25b is well-tested with p4a + Kivy 2.3.1 and API 34.
android.ndk     = 25b
android.ndk_api = 24

# CPU architectures included in the APK
android.archs = arm64-v8a, armeabi-v7a

# Automatically accept the SDK license prompt during build
android.accept_sdk_license = True

# Keep user data (usuarios.json, listas_*.json, precios_globales.json) on
# Android's standard app-private storage, and allow Android auto-backup.
android.private_storage = True
android.allow_backup    = True

# Emit Android logcat lines filtered to Python and the Kivy logger
android.logcat_filters  = *:S python:D

# ─────────────────────────────────────────────────────────────────────────
#  python-for-android
# ─────────────────────────────────────────────────────────────────────────
# Force the SDL2 bootstrap (default, but explicit is safer)
p4a.bootstrap = sdl2

# Leave p4a.branch at its default; pinning it is only needed when a
# specific p4a fix has not landed in a release yet.
#p4a.branch = master

# ─────────────────────────────────────────────────────────────────────────
#  iOS  (not used on GitHub Actions — left here for parity with the template)
# ─────────────────────────────────────────────────────────────────────────
# ios.kivy_ios_dir      = ../kivy-ios
# ios.codesign.debug    = "iPhone Developer: <lastname> <firstname> (<hex>)"
# ios.codesign.release  = %(ios.codesign.debug)s

# ─────────────────────────────────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────────────────────────────────
# 1 = normal, 2 = verbose. Set to 2 only when debugging a build.
log_level = 1

# ─────────────────────────────────────────────────────────────────────────
#  Buildozer / Gradle extras (all optional — commented out on purpose)
# ─────────────────────────────────────────────────────────────────────────
# android.add_jars              = foo.jar,bar.jar
# android.add_src               =
# android.add_aars              =
# android.gradle_dependencies   =
# android.add_activities        =
# android.manifest_placeholders =
# android.add_compile_options   =
# android.whitelist             =
# android.whitelist_src         =
# android.blacklist_src         =
# android.add_libs_armeabi      = libs/android/*.so
# android.add_libs_armeabi_v7a  = libs/android-v7/*.so
# android.add_libs_arm64_v8a    = libs/android-v8/*.so
# android.add_libs_x86          = libs/android-x86/*.so
# android.add_libs_x86_64       = libs/android-x64/*.so
# android.enable_androidx       = True
# android.wakelock              = False