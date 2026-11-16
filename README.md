## MirandaList



## Metodología de investigación
   Link Encuesta: https://forms.gle/fUqRz53M5f1b9C176

   Resultados Encuesta: https://docs.google.com/spreadsheets/d/17e4VL_yqJxEj8KFdAcIP1bdYK6tSLGgyYaiQ9mujS3k/edit?usp=sharing

## Estructura del proyecto Cyro-punch

Este repositorio contiene una aplicación de listas de compras desarrollada con Python y Kivy/KivyMD.



## Descripción de los archivos principales

### `main.py`
Es el archivo central de la aplicación.

Aquí se define:
- la lógica de la app con Kivy
- las pantallas y flujos de navegación
- la gestión de listas, productos y notas
- la persistencia de datos en `listas.json`
- la configuración visual, temas y traducciones

En otras palabras, este archivo concentra la parte funcional y del comportamiento del programa.

### `listas.json`
Es el archivo de almacenamiento local.

Se usa para guardar:
- las listas creadas por el usuario
- los productos asociados a cada lista
- el tipo de lista (checklist o notepad)
- el estado de artículos marcados o pendientes
- datos como nombre, comercio y notas

Es la base de datos sencilla del proyecto mientras la app está siendo usada.


## Resumen

El proyecto está organizado como una aplicación móvil/desktop pequeña con una estructura muy directa:

- lógica de negocio en `main.py`
- interfaz en `interfaz.kv`
- almacenamiento local en `listas.json`
- documentación y dependencias en los otros archivos
