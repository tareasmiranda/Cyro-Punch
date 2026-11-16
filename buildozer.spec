[app]
version = 1.0
title = Cyro-Punch
package.name = cyropunch
package.domain = org.cyropunch

source.dir = .
source.include_exts = py,png,jpg,kv,json,ttf,txt,md

# KivyMD + Plyer for notifications
requirements = python3,kivy==2.3.1,kivymd==2.0.0,plyer

# Android permissions (optional but recommended)
android.permissions = INTERNET, VIBRATE

# Orientation and fullscreen
orientation = portrait
fullscreen = 1

# Android API levels (adjust if needed)
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
