# Uso de IA en el desarrollo de la app de lista de compras

Este documento registra cómo se ha utilizado inteligencia artificial (Claude, de Anthropic) durante el desarrollo de la app móvil, qué se ha trabajado con su ayuda y qué decisiones se tomaron. Se actualiza cada vez que se integra una nueva funcionalidad.

- **Proyecto:** App móvil de lista de compras (Compra semanal, Inicio, Listas, Ajustes)
- **Tecnologías:** Python, Kivy, KivyMD
- **Entorno:** venv en Windows
- **Herramienta de IA:** Claude (Anthropic)
- **Última actualización:** 2026-10-05

---

## 1. Resumen del proyecto

Aplicación móvil sencilla para almacenar y organizar pedidos de compras. El desarrollo partió de capturas de diseño previamente elaboradas, y la fase actual se centra únicamente en el **diseño visual** (layout, botones, colores y elementos). Todavía no se busca que sea 100 % funcional.

## 2. Rol de la IA en el proyecto

La IA se usó como asistente de programación para:

- Traducir las capturas de diseño a código Kivy/KivyMD.
- Reorganizar la estructura del proyecto.
- Implementar funcionalidades de interfaz (idioma y tema).
- Corregir errores visuales puntuales.

Las decisiones de diseño, los requisitos y la validación del resultado son responsabilidad del desarrollador; la IA propone y genera código que luego se revisa y prueba.

## 3. Registro de funcionalidades y trabajo asistido por IA

| # | Funcionalidad / tarea | Descripción | Estado |
|---|-----------------------|-------------|--------|
| 1 | Diseño base de la interfaz | Construcción de pantallas (Compra semanal, Inicio, Listas, Ajustes) a partir de capturas de diseño, usando Kivy y KivyMD | Hecho |
| 2 | Separación de archivos | División del proyecto en `main.py` (lógica de negocio y backend) y un archivo `.kv` (diseño y jerarquías visuales), manteniendo la misma apariencia y lógica | Hecho |
| 3 | Cambio de idioma (ES/EN) | Menú desplegable al presionar "Idioma" para alternar entre Español e Inglés | Hecho |
| 4 | Modo claro / oscuro | Oscuro por defecto; solo alterna al presionar el botón, con transición suave y los mismos colores y tonos en ambos modos | Hecho |
| 5 | Corrección de color de texto | Los botones "Nueva lista" y "Agregar" quedaban con texto blanco tras alternar oscuro → claro → oscuro | Corregido |
| 6 | Ajustes del menú de idioma | El menú se abre alineado a la derecha y con una transición leve al desplegarse | Hecho |

## 4. Flujo de trabajo con la IA

1. Se describe el requerimiento (o se comparte una captura de diseño).
2. La IA genera o modifica el código correspondiente.
3. El desarrollador prueba en su entorno (venv, Windows) y reporta errores o ajustes.
4. Se itera hasta que el resultado coincide con lo esperado.

## 5. Buenas prácticas y consideraciones

- Revisar y probar todo el código generado antes de integrarlo.
- Mantener la separación entre lógica (`main.py`) y diseño (`.kv`).
- Registrar en este documento cada funcionalidad nueva, indicando qué se pidió y cómo se resolvió.
- Las partes del proyecto elaboradas con apoyo de IA deben declararse según lo exija la normativa de la asignatura o institución.

## 6. Historial de actualizaciones

| Fecha | Cambio |
|-------|--------|
| 2026-10-05 | Creación del documento con el trabajo realizado hasta la fecha (funcionalidades 1 a 6) |

---

## Plantilla para nuevas funcionalidades

Al integrar una nueva funcionalidad, agregar una fila en la tabla de la sección 3 y una entrada en la sección 6:

```
| N | Nombre de la funcionalidad | Qué se pidió y cómo se resolvió | Estado |
```
