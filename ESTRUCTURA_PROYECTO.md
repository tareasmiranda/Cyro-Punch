# Estructura del proyecto Cyro-punch

Este repositorio contiene una aplicación de listas de compras desarrollada con Python y Kivy/KivyMD. La app organiza compras, listas de tareas y notas, y guarda la información localmente en un archivo JSON para mantener los datos entre ejecuciones.

## Árbol del proyecto

```text
Cyro-punch/
├── .gitignore
├── README.md
├── main.py
├── interfaz.kv
├── listas.json
├── requirements.txt
├── venv/
├── docs/
│   ├── AI-WORKFLOW.md
│   └── uso-de-IA.md
└── .git/
```

## Descripción de los archivos principales

### 1) `main.py`
Es el archivo central de la aplicación.

Aquí se define:
- la lógica de la app con Kivy
- las pantallas y flujos de navegación
- la gestión de listas, productos y notas
- la persistencia de datos en `listas.json`
- la configuración visual, temas y traducciones

En otras palabras, este archivo concentra la parte funcional y del comportamiento del programa.

### 2) `interfaz.kv`
Es el archivo de interfaz gráfica de Kivy.

Aquí se especifican:
- la estructura visual de la app
- los widgets y sus propiedades
- el diseño de pantallas, botones, listas y formularios
- estilos y distribución de elementos en la interfaz

Este archivo trabaja junto con `main.py`, donde la lógica carga y conecta la UI con la funcionalidad.

### 3) `listas.json`
Es el archivo de almacenamiento local.

Se usa para guardar:
- las listas creadas por el usuario
- los productos asociados a cada lista
- el tipo de lista (checklist o notepad)
- el estado de artículos marcados o pendientes
- datos como nombre, comercio y notas

Es la base de datos sencilla del proyecto mientras la app está siendo usada.

### 4) `requirements.txt`
Contiene las dependencias del proyecto.

Incluye los paquetes necesarios para ejecutar la aplicación, principalmente:
- Kivy
- KivyMD

Esto permite instalar fácilmente todas las librerías requeridas con pip.

### 5) `README.md`
Es la documentación general del repositorio.

En este archivo se suelen encontrar:
- descripción del proyecto
- objetivos y uso general
- instrucciones de instalación
- pasos para ejecutar la app
- información básica para usuarios y desarrolladores

### 6) `docs/`
Carpeta de documentación adicional.

Incluye archivos relacionados con:
- flujo de trabajo con IA
- uso de inteligencia artificial en el proyecto
- documentación técnica o de proceso

#### Archivos dentro de `docs/`
- `AI-WORKFLOW.md`: describe el flujo de trabajo del proyecto o su uso con IA.
- `uso-de-IA.md`: explica cómo se utiliza la IA dentro del contexto del desarrollo.

### 7) `.gitignore`
Archivo de configuración git.

Se usa para ignorar archivos o carpetas que no deben subirse al repositorio, como por ejemplo:
- entorno virtual (`venv/`)
- archivos temporales
- artefactos de ejecución

### 8) `venv/`
Carpeta del entorno virtual de Python.

Aquí se instalan las librerías del proyecto sin afectar el entorno global del sistema. Es útil para mantener un entorno limpio y reproducible.

## Relación entre archivos

La arquitectura es bastante simple y clara:

- `main.py` contiene la lógica principal.
- `interfaz.kv` define cómo se ve la aplicación.
- `listas.json` guarda la información del usuario.
- `requirements.txt` define las dependencias.
- `README.md` explica cómo empezar a usar el proyecto.
- `docs/` guarda documentación complementaria.

## Resumen

El proyecto está organizado como una aplicación móvil/desktop pequeña con una estructura muy directa:

- lógica de negocio en `main.py`
- interfaz en `interfaz.kv`
- almacenamiento local en `listas.json`
- documentación y dependencias en los otros archivos

Si quieres, también puedo crear una segunda versión de este archivo con un formato más técnico o con un diagrama visual del flujo de la app.
