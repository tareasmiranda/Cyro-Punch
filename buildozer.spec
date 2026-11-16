[app]
title = Lista de compras
package.name = listacompras
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf

version = 0.1
requirements = python3,kivy,kivymd,plyer

orientation = portrait
fullscreen = 0

# Permissions needed for notifications (Android 13+)
android.permissions = POST_NOTIFICATIONS

# Recommended API/NDK for current Buildozer versions
android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a