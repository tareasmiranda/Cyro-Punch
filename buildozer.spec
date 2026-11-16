[app]
title = Miranda Organizer
package.name = mirandaorganizer
package.domain = org.mirandaorganizer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = assets/*
version = 1.0

# Keep KivyMD 2.0.0 so your main.py and interfaz.kv remain valid.
requirements = python3,kivy==2.3.1,kivymd==2.0.0,plyer,materialyoucolor,exceptiongroup,asyncgui,asynckivy

orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/assets/icon.png
android.permissions = INTERNET
android.archs = arm64-v8a, armeabi-v7a
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
p4a.branch = master
source.exclude_patterns = buildozer.spec,.git/**,__pycache__/**,*.pyc,venv/**,.github/**