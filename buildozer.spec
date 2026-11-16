[app]
# (str) Title of your application
title = Miranda Organizer

# (str) Package name (reverse domain notation)
package.name = mirandaorganizer

# (str) Package domain
package.domain = org.mirandaorganizer

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Patterns of files to include (for assets folder)
source.include_patterns = assets/*

# (str) Application versioning
version = 1.0

# (list) Application requirements
requirements = python3,kivy,kivymd,plyer,materialyoucolor,exceptiongroup,asyncgui,asynckivy

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

# (str) Application icon (path relative to source.dir)
icon.filename = %(source.dir)s/assets/icon.png

# (list) Android specific permissions
android.permissions = INTERNET

# (list) Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (str) Android API to use
android.api = 31

# (str) Android minimum API
android.minapi = 21

# (str) Android NDK version
android.ndk = 23b

# (str) Android SDK version
android.sdk = 24

# (str) P4A branch
p4a.branch = master

# (list) Patterns of files to exclude
source.exclude_patterns = buildozer.spec,.git/**,__pycache__/**,*.pyc,venv/**,.github/**