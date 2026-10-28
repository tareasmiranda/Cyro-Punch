## MirandaList

MirandaOrganizer es una aplicación orientada a usuarios que buscan organizar y administrar sus compras semanales de manera sencilla, clara y eficiente. Está diseñada considerando especialmente las necesidades de personas que valoran la planificación y el orden en sus actividades cotidianas, sin interrupciones molestas como publicidad que pueda distraerte de lo que realmente necesitas hacer para mejorar tu productividad.

Su principal elemento diferenciador frente a otras aplicaciones de listas de compras es que su desarrollo se basa en las opiniones, necesidades y experiencias de los propios usuarios, buscando ofrecer una herramienta práctica, accesible y adaptada a sus hábitos de compra.

## Metodología de investigación
   Link Encuesta: https://forms.gle/fUqRz53M5f1b9C176

   Resultados Encuesta: https://docs.google.com/spreadsheets/d/17e4VL_yqJxEj8KFdAcIP1bdYK6tSLGgyYaiQ9mujS3k/edit?usp=sharing

## Instrucciones de instalación
Para usar la aplicación, siga los siguientes pasos de instalación desde el repositorio o portable, según sus sistema operativo:
### Windows

1. Clona el repositorio ejecutando 
```git clone https://github.com/tareasmiranda/Cyro-punch.git```
2. Accede a la carpeta```cd Cyro-punch```
3. Crea un entorno virtual de Python ejecutando```python -m venv venv```
4. Activa el entorno virtual ejecutando ```venv\Scripts\activate```
5. Instala las dependencias ejecutando ```pip install --upgrade pip``` 
```pip install -r requirements.txt```
6. Una vez instalado, puedes lanzar la aplicación en consola con ```python main.py```

### Linux

1. Clona el repositorio ejecutando ```git clone https://github.com/tareasmiranda/Cyro-punch.git;cd Cyro-punch```
2. Crea un entorno virtual de Python ejecutando ```python3 -m venv venv```
3. Activa el entorno virtual ejecutando ```source venv/bin/activate```
4. Instala las dependencias ejecutando ```pip install --upgrade pip;pip install -r requirements.txt```
5. Una vez instalado, puedes lanzar la aplicación con ```python main.py```

## Estructura del proyecto Cyro-punch

Este repositorio contiene una aplicación de listas de compras desarrollada con Python y Kivy/KivyMD.

### Árbol del proyecto

```
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

### `main.py`
Es el archivo central de la aplicación.

Aquí se define:
- la lógica de la app con Kivy
- las pantallas y flujos de navegación
- la gestión de listas, productos y notas
- la persistencia de datos en `listas.json`
- la configuración visual, temas y traducciones

En otras palabras, este archivo concentra la parte funcional y del comportamiento del programa.

### `interfaz.kv`
Es el archivo de interfaz gráfica de Kivy.

Aquí se especifican:
- la estructura visual de la app
- los widgets y sus propiedades
- el diseño de pantallas, botones, listas y formularios
- estilos y distribución de elementos en la interfaz

Este archivo trabaja junto con `main.py`, donde la lógica carga y conecta la UI con la funcionalidad.

### `listas.json`
Es el archivo de almacenamiento local.

Se usa para guardar:
- las listas creadas por el usuario
- los productos asociados a cada lista
- el tipo de lista (checklist o notepad)
- el estado de artículos marcados o pendientes
- datos como nombre, comercio y notas

Es la base de datos sencilla del proyecto mientras la app está siendo usada.

### `requirements.txt`
Contiene las dependencias del proyecto.

Incluye los paquetes necesarios para ejecutar la aplicación, principalmente:
- Kivy
- KivyMD

Esto permite instalar fácilmente todas las librerías requeridas con pip.

## Resumen

El proyecto está organizado como una aplicación móvil/desktop pequeña con una estructura muy directa:

- lógica de negocio en `main.py`
- interfaz en `interfaz.kv`
- almacenamiento local en `listas.json`
- documentación y dependencias en los otros archivos
