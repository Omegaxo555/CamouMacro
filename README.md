# CamouMacro

CamouMacro es un proyecto para automatizar formularios web con Camoufox + Playwright, usando perfiles persistentes, un navegador tipo tablet y una interfaz de terminal para seleccionar diferentes algoritmos o flujos de automatización.

## Índice

- Requisitos
- Instalación
- Generar la plantilla de perfil
- Ejecutar el proyecto
- Estructura del proyecto
- Documentación de clases
- Ejemplos de uso
- Solución de problemas

## Requisitos

- Python 3.10+
- Git
- Entorno virtual recomendado
- Tor opcional, si quieres usar proxy SOCKS
- Firefox instalado o gestionado por Camoufox

## Instalación

### 1) Crear el entorno virtual

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Instalar dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si no tienes `requirements.txt`, puedes instalar las dependencias manualmente:

```bash
python -m pip install camoufox playwright
```

### 3) Instalar el Firefox de Camoufox

```bash
camoufox fetch
```

o, si no está en PATH:

```bash
python -m camoufox fetch
```

## Generar la plantilla de perfil

El proyecto usa una plantilla de perfil comprimida en:

```text
templates/perfil_base.tar.gz
```

Puedes generarla con:

```bash
python generate_profile_template.py
```

Ese script crea un perfil persistente con una ventana tipo tablet vertical, lo comprime en `.tar.gz` y lo deja listo para que el navegador lo use al iniciarse.

## Ejecutar el proyecto

```bash
python main.py
```

Al arrancar, el programa:

1. inicia Camoufox
2. abre una ventana flotante tipo tablet vertical
3. muestra un menú en consola para elegir el algoritmo/flujo a ejecutar
4. ejecuta la acción seleccionada
5. cierra la sesión al terminar

## Estructura del proyecto

```text
CamouMacro/
├── main.py
├── README.md
├── requirements.txt
├── generate_profile_template.py
├── templates/
│   └── perfil_base.tar.gz
├── core/
│   ├── __init__.py
│   └── camoufox_handler.py
├── modules/
│   ├── __init__.py
│   └── form_automator.py
├── config/
│   └── settings.py
└── .venv/
```

## Documentación de clases

### 1) CamoufoxHandler

Archivo: `core/camoufox_handler.py`

Esta clase encapsula la lógica de inicialización del navegador y del perfil persistente.

#### Propósito

- preparar el perfil temporal
- lanzar Camoufox con configuración útil para automatización web
- abrir una página en el contexto del navegador
- navegar por URLs
- cerrar y limpiar recursos temporales

#### Constructor

```python
handler = CamoufoxHandler(
    proxy_server="socks5://127.0.0.1:9050",
    tor_proxy="socks5://127.0.0.1:9050",
    profile_template="templates/perfil_base.tar.gz",
    headless=False,
    timeout=30,
    window_size=(600, 900),
)
```

Parámetros:

- `proxy_server`: servidor proxy si quieres forzar tráfico por proxy externo
- `tor_proxy`: alias para mantener compatibilidad con el proyecto
- `profile_template`: ruta al tar.gz con el perfil base
- `headless`: si se abre sin interfaz visual
- `timeout`: timeout por defecto del navegador
- `window_size`: tamaño de la ventana, por defecto `(600, 900)`

#### Métodos principales

##### `is_tor_available(host="127.0.0.1", port=9050)`

Comprueba si Tor está escuchando en el puerto configurado.

```python
if CamoufoxHandler.is_tor_available():
    print("Tor disponible")
else:
    print("Tor no disponible")
```

##### `initialize()`

Inicializa el navegador, crea el contexto persistente si existe una plantilla y abre la primera página de trabajo.

```python
if handler.initialize():
    print("Navegador listo")
```

##### `navigate(url, max_retries=3)`

Navega a una URL y reintenta varias veces si falla por red.

```python
handler.navigate("https://httpbin.org/forms/post")
```

##### `verify_ip()`

Verifica si la navegación pasa por Tor o si la conexión es normal.

```python
handler.verify_ip()
```

##### `close()`

Cierra el navegador y borra el directorio temporal del perfil.

```python
handler.close()
```

#### Ejemplo completo

```python
from core.camoufox_handler import CamoufoxHandler

handler = CamoufoxHandler(
    profile_template="templates/perfil_base.tar.gz",
    headless=False,
    window_size=(600, 900),
)

if handler.initialize():
    handler.navigate("https://example.com")
    handler.verify_ip()
    handler.close()
```

---

### 2) FormAutomator

Archivo: `modules/form_automator.py`

Esta clase se encarga de interactuar con elementos HTML dentro de una página Playwright.

#### Propósito

- escribir texto con pausas humanas
- hacer clic sobre botones y elementos
- seleccionar opciones en dropdowns
- completar formularios en masa
- enviar formularios y esperar resultados

#### Constructor

```python
from modules.form_automator import FormAutomator

automator = FormAutomator(page)
```

#### Métodos principales

##### `human_type(selector, text, clear_first=True, min_delay=50, max_delay=120)`

Escribe texto de forma más humana, con pausas aleatorias entre caracteres.

```python
automator.human_type("input[name='custname']", "Alex Ruiz")
```

Parámetros:

- `selector`: selector CSS del input
- `text`: texto a escribir
- `clear_first`: si se debe borrar el contenido antes de escribir
- `min_delay`: mínimo de espera entre caracteres
- `max_delay`: máximo de espera entre caracteres

##### `safe_click(selector, timeout=5000)`

Hace clic en un elemento visible, con comprobaciones de estado.

```python
automator.safe_click("button[type='submit']")
```

##### `select_dropdown_option(selector, value_or_label)`

Selecciona una opción dentro de un `select`.

```python
automator.select_dropdown_option("select[name='country']", "MX")
```

##### `fill_form_dict(form_data)`

Rellena varios campos de un formulario pasando un diccionario.

```python
form_data = {
    "input[name='custname']": "Alex Ruiz",
    "input[name='custemail']": "alex@example.com",
    "textarea[name='comments']": "Mensaje de prueba",
}

automator.fill_form_dict(form_data)
```

##### `submit_form(submit_selector, expected_url_part=None, success_selector=None, timeout=10000)`

Hace clic en el botón de envío y espera a que el formulario termine.

```python
automator.submit_form(
    submit_selector="button[type='submit']",
    expected_url_part="/success",
    timeout=10000,
)
```

#### Ejemplo completo

```python
from modules.form_automator import FormAutomator

page = driver.page
automator = FormAutomator(page)

automator.human_type("input[name='custname']", "Alex Ruiz")
automator.human_type("input[name='custemail']", "alex@example.com")
automator.safe_click("button[type='submit']")
```

---

## Ejemplos de uso

### Ejemplo 1: abrir navegador y navegar

```python
from core.camoufox_handler import CamoufoxHandler

handler = CamoufoxHandler(
    profile_template="templates/perfil_base.tar.gz",
    headless=False,
    window_size=(600, 900),
)

handler.initialize()
handler.navigate("https://example.com")
handler.close()
```

### Ejemplo 2: completar un formulario

```python
from core.camoufox_handler import CamoufoxHandler
from modules.form_automator import FormAutomator

handler = CamoufoxHandler(
    profile_template="templates/perfil_base.tar.gz",
    headless=False,
    window_size=(600, 900),
)

if handler.initialize():
    handler.navigate("https://httpbin.org/forms/post")
    automator = FormAutomator(handler.page)
    automator.human_type("input[name='custname']", "Alex Ruiz")
    automator.human_type("input[name='custemail']", "alex@example.com")
    automator.human_type("textarea[name='comments']", "Autorizado por CamouMacro")
    automator.safe_click("input[type='submit']")
    handler.close()
```

### Ejemplo 3: usar el menú del programa principal

```bash
python main.py
```

Desde el menú de terminal podrás elegir:

- formulario de prueba
- salir

## Resolución de problemas

### Error: `profile_template` no existe

```text
No se pudo encontrar la plantilla de perfil.
```

Solución:

```bash
python generate_profile_template.py
```

### Error: Tor no está disponible

Si ves un warning de que no hay proxy o Tor no está levantado, entonces lo normal es que se inicie sin proxy. Si quieres usar Tor, debes arrancarlo antes:

```bash
tor
```

### Error: `CamoufoxNotInstalled`

```text
official/stable is not installed
```

Solución:

```bash
camoufox fetch
```

### El navegador se abre demasiado grande

El proyecto ya está configurado para abrir una ventana tipo tablet vertical:

```python
window_size=(600, 900)
```

Eso te da un aspecto flotante, más estrecho y más alto que una ventana normal.

## Notas finales

- La plantilla del perfil sirve para reutilizar el estado del navegador.
- La ventana queda orientada a tablet vertical para simular un dispositivo móvil/tabla.
- El flujo principal usa un menú de consola para elegir qué algoritmo o módulo ejecutar.

## Licencia

Este proyecto está pensado para uso educativo y de automatización local. Asegúrate de respetar los términos de uso de las páginas que automatices.
