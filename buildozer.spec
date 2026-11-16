name: Build Miranda Organizer

on:
  push:
    branches-ignore:
      - data
      - gh-pages
    tags:
      - '**'
  pull_request:
    branches-ignore:
      - data
      - gh-pages

jobs:
  build-android:
    name: Build for Android
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          path: main   # Checkout into a folder named 'main' to match the branch

      - name: Build with Buildozer
        uses: ArtemSBulgakov/buildozer-action@v1
        id: buildozer
        with:
          repository_root: main   # Use the folder from the checkout step
          workdir: .
          command: buildozer android debug
          buildozer_version: stable

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: package
          path: ${{ steps.buildozer.outputs.filename }}