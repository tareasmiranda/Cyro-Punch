[app]

# (str) Title of your application
title = Lista de compras

# (str) Package name
package.name = listacompras

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,ttf

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
# source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# IMPORTANT: pin KivyMD to 1.1.1 — the 2.x / master branch depends on
# pycairo (via MaterialShapes), which has no python-for-android recipe
# and breaks the Android build.
requirements = python3,kivy==2.3.1,kivymd==1.1.1,pillow,sdl2_ttf==2.0.15

# (str) Custom source folders for requirements
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
# garden_requirements = mapping

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# POST_NOTIFICATIONS is required for local notifications on Android 13+
android.permissions = POST_NOTIFICATIONS

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support,
# it should usually be the same as android.minapi.
#android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
# android.skip_update = False

# (bool) If True, then automatically accept SDK license agreements
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (list) Pattern to whitelist for the .apk packaging
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process.
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =

# (list) Android AAR archives to add (currently works only with sdl2 bootstrap)
#android.add_aars =

# (list) Gradle dependencies to add (currently works only with sdl2 bootstrap)
#android.gradle_dependencies =

# (bool) adds permission to your AndroidManifest.xml
#android.add_activities =

# (list) Android manifest placeholders
#android.manifest_placeholders =

# (list) add java compile options
#android.add_compile_options =

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) python-for-android specific commit to use, defaults to HEAD
#p4a.commit = HEAD

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (int) Android API to use for the build
#android.api = 34

# (bool) enables Android auto backup feature (Android API >=23)
#android.allow_backup = True

# (str) XML file to include as an intent filters in <activity> tag
#android.manifest.intent_filters =

# (str) launchMode to set for the main activity
#android.manifest.launch_mode = standard

# (list) Android additional libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_arm64_v8a = libs/android-v8/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_x86_64 = libs/android-x64/*.so

# (bool) Indicate whether the screen should stay on
#android.wakelock = False

# (list) Python for Android recipes to use (space separated)
#p4a.recipes =

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
#android.arch = armeabi-v7a

# (int) overrides automatic versionCode
#android.numeric_version = 1

# (bool) enables Android auto backup feature (Android API >=23)
#android.allow_backup = True

#
# Python for android (p4a) specific
#
# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes =

# (str) Filename to the hook for p4a
#p4a.hook =

# (str) Bootstrap to use for android builds
#p4a.bootstrap = sdl2

#
# iOS specific
#
# (str) Path to a custom kivy-ios folder
#ios.kivy_ios_dir = ../kivy-ios

# (str) Name of the certificate to use for signing the debug version
#ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = %(ios.codesign.debug)s

#
# Android specific
#
# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process.
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =

# (list) Android AAR archives to add (currently works only with sdl2 bootstrap)
#android.add_aars =

# (list) Gradle dependencies to add (currently works only with sdl2 bootstrap)
#android.gradle_dependencies =

# (bool) adds permission to your AndroidManifest.xml
#android.add_activities =

# (list) Android manifest placeholders
#android.manifest_placeholders =

# (list) add java compile options
#android.add_compile_options =

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) python-for-android specific commit to use, defaults to HEAD
#p4a.commit = HEAD

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
#android.arch = armeabi-v7a

# (int) overrides automatic versionCode
#android.numeric_version = 1

# (bool) enables Android auto backup feature (Android API >=23)
#android.allow_backup = True

#
# Android Logcat
#
# (list) Android logcat filters to use
#android.logcat_filters = *:S python:D

#
# Buildozer
#
# (str) Buildozer log level, choices are 1 (default) to 2 (debug)
#log_level = 1

# (str) Run the app on the device after build
#android.run = False

# (str) Automatically start the app on the device
#android.autostart = False

# (list) List of available architectures
#android.archs = armeabi-v7a, arm64-v8a

# (bool) Enable AndroidX support.
#android.enable_androidx = True

# (str) Kotlin version to use
#android.kotlin_version = 1.3.72

# (list) Android additional libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_arm64_v8a = libs/android-v8/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_x86_64 = libs/android-x64/*.so