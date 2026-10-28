# Uso de IA en el proyecto: Lista de compras (Kivy + KivyMD)

Registro de las funcionalidades desarrolladas con ayuda de IA (Claude).
Se actualiza cada vez que se integra una funcionalidad nueva.

| N.º | Funcionalidad | Archivos |
|-----|---------------|----------|
| 1 | Diseño base de las cuatro pantallas (Inicio, Listas, Detalle, Ajustes) a partir de las capturas del diseño | `main.py`, `interfaz.kv` |
| 2 | Separación del proyecto: lógica en `main.py` y diseño/jerarquía visual en `interfaz.kv` | `main.py`, `interfaz.kv` |
| 3 | Idioma Español/Inglés con menú desplegable al presionar "Idioma" | `main.py`, `interfaz.kv` |
| 4 | Modo oscuro/claro (oscuro por defecto) con transición suave y los mismos tonos en ambos modos | `main.py`, `interfaz.kv` |
| 5 | Corrección del color del texto de los botones "Nueva lista" y "Agregar" tras alternar el tema | `main.py`, `interfaz.kv` |
| 6 | Ajuste del menú de idioma: alineado a la derecha y con transición leve al abrirse | `main.py` |
| 7 | Funcionalidad de "Nueva lista" / "Agregar": formulario (nombre, comercio, tipo Checklist o Notepad), edición de listas y persistencia en `listas.json` | `main.py`, `interfaz.kv` |
| 8 | Corrección del checklist: artículos apilados hacia abajo y pantalla adaptable a distintos tamaños; el campo cantidad pasa a ser precio (placeholder `$`, solo números) | `main.py`, `interfaz.kv` |
| 9 | Total de la compra en el checklist, tipo de lista bloqueado al editar y cuadro de texto del Notepad ajustado a todo el espacio disponible | `main.py`, `interfaz.kv` |
| 10 | Autorreparación de la pantalla de detalle (lista invisible y botones editar/volver sin respuesta de forma intermitente) y aviso en consola | `main.py` |

## Detalle de la funcionalidad 7

- Los botones "Nueva lista" (Inicio) y "Agregar" (Listas) abren la misma ventana,
  que además se reutiliza como "Editar lista" desde el detalle (ícono de lápiz).
- La lista nueva exige un nombre; el comercio es opcional. Al crearla se abre su detalle.
- Tipos de lista: **Checklist** (artículos con casilla, progreso, agregar y quitar)
  y **Notepad** (texto libre que se guarda mientras se escribe).
- Una lista se puede editar (nombre, comercio, tipo) y eliminar (con confirmación
  de doble toque).
- Persistencia: todas las listas se guardan en `listas.json`. En escritorio queda
  junto a `main.py`; en Android/iOS, en la carpeta de datos privada de la app.
  La escritura es atómica (archivo temporal + reemplazo) y, si el archivo estuviera
  dañado, se conserva una copia con extensión `.dañado` y la app arranca vacía.
- Se guarda al crear, editar, marcar/agregar/quitar artículos, al pausar la app
  y al cerrarla.

## Detalle de la funcionalidad 8

- **Apilado:** al agregar un producto se forzaba el scroll al final; con pocos
  artículos eso dejaba la lista pegada abajo del área visible (se veía apilada
  hacia arriba). Ahora el scroll solo baja si la lista ya no cabe, y vuelve arriba
  cuando cabe (al agregar, quitar o cambiar el tamaño de la ventana).
- **Responsive:** el cuerpo del detalle ocupa el alto disponible, sin huecos de
  separación por widgets ocultos, y los campos de nombre y precio se reparten el
  ancho en proporción. Se revisó en ventanas de 360x640, 392x800 y 412x915.
- **Precio:** reemplaza a la cantidad. Solo acepta números (teclado numérico en el
  móvil), se muestra como `$1.990` en cada artículo y se guarda como dígitos en el
  JSON (`"price"`). Las listas guardadas con `"quantity"` se cargan sin precio.

## Detalle de la funcionalidad 9

- **Total de la compra:** en las listas Checklist se muestra, sobre el campo de
  agregar producto, la suma de los precios de todos los artículos (marcados o no),
  con formato `$7.770`. Se actualiza al agregar, quitar o editar artículos.
- **Editar lista:** ya no aparece el selector de tipo; el tipo se elige solo al
  crear la lista y no cambia después (tampoco por código al guardar los cambios).
- **Notepad:** el cuadro de texto ocupa todo el alto disponible, con el mismo
  margen inferior que el resto de las pantallas, y cualquier toque dentro de la
  tarjeta enfoca el texto (antes solo respondía sobre el texto). En el móvil,
  al abrir el teclado la interfaz se encoge para caber sobre él
  (`softinput_mode = "resize"`).

## Detalle de la funcionalidad 10

- **Síntoma:** a veces, al abrir una lista Checklist, los artículos no se ven (aunque
  el total y el campo de agregar sí) y los botones de editar y volver no responden;
  a veces se arregla reiniciando la app.
- **Diagnóstico:** el primer intento (transición de pantalla colgada) quedó descartado
  con la captura (el campo de agregar respondía). La consola del usuario mostró el dato
  clave: el `ScrollView` de la lista medía **0 de alto** (`size=(430,0)`) aunque el
  contenido existía (515 de alto) y había espacio de sobra, con escala de pantalla de
  Windows de 125 %. Un alto 0 con espacio libre significa que el tamaño del `ScrollView`
  no seguía a su regla (`size_hint_y` en `None` en vez de `1`).
- **Causa probable:** la lista y el bloc de notas estaban siempre en pantalla y se
  alternaban con reglas de `.kv` que cambiaban `size_hint_y`, `opacity` y `disabled`.
  No se logró reproducir el estado roto en la ventana simulada, pero esa mecánica es
  frágil y coincide con el síntoma.
- **Cambios:**
  - La lista (`ItemsScroll`) y el bloc de notas (`NotesCard`) pasan a ser dos clases
    del `.kv` que `main.py` crea una vez y coloca en el contenedor `body` del detalle
    con `_show_body()`: en pantalla hay solo uno, sin ocultar con tamaño 0, opacidad
    ni `disabled`.
  - La lista sigue siendo un `GridLayout` que apila de arriba hacia abajo y mide al
    menos el alto visible.
  - `ui_check()` revisa tras cada cambio de pantalla, al redimensionar y al volver de
    segundo plano: que no haya una transición colgada ni pantallas de más, que un
    toque sobre los botones de arriba llegue a esos botones y que se vea algún
    artículo. Si la lista queda sin alto, la reconstruye, fuerza `size_hint_y = 1` y
    escribe `UI auto-reparada: ...` con tamaños, `size_hint_y`, ventana y densidad;
    luego confirma si funcionó. Se ejecuta una sola vez por apertura (sin bucle).
- **Verificación:** se reprodujo a propósito el estado de la consola (`ScrollView` con
  alto 0 y `size_hint_y = None`, densidad 1.25, ventana de 490x1000): la revisión lo
  detecta, lo repara y la lista vuelve a medir 497. Capturas del Checklist y del
  Notepad en 392x800 y 360x640, y 16 corridas aleatorias con toques reales sin avisos.
