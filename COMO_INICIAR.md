# Guía de Inicio Rápido - CamouMacro

Esta guía detalla paso a paso cómo poner en marcha el proyecto **CamouMacro** desde una computadora que recién acaba de descargar o clonar el repositorio y no cuenta con ninguna dependencia configurada previamente.

---

## 📌 Tabla de Contenidos
1. [Requisitos Mínimos](#1-requisitos-mínimos)
2. [Instalación Rápida Paso a Paso (PC limpia)](#2-instalación-rápida-paso-a-paso-pc-limpia)
   - [Opción 1: Instalación Standalone en Windows (Recomendada para uso nativo)](#opción-1-instalación-standalone-en-windows-recomendada-para-uso-nativo)
   - [Opción 2: Instalación Manual con Python](#opción-2-instalación-manual-con-python)
   - [Opción 3: Despliegue con Docker (Cero dependencias)](#opción-3-despliegue-con-docker-cero-dependencias)
3. [Configuración de Objetivos y Género (profiles_dict.txt)](#3-configuración-de-objetivos-y-género-profiles_dicttxt)
4. [Cómo Abrir y Ejecutar el Algoritmo (Formas de Inicio)](#4-cómo-abrir-y-ejecutar-el-algoritmo-formas-de-inicio)
   - [Método A: Panel de Control de Escritorio (GUI Tkinter)](#método-a-panel-de-control-de-escritorio-gui-tkinter)
   - [Método B: Menú Interactivo en Terminal (main.py)](#método-b-menú-interactivo-en-terminal-mainpy)
   - [Método C: Ejecución por Consola con Parámetros (runner.py)](#método-c-ejecución-por-consola-con-parámetros-runnerpy)
   - [Método D: Dashboard Interactivo en Go (TUI Bubbletea)](#método-d-dashboard-interactivo-en-go-tui-bubbletea)
   - [Método E: CLI en Go](#método-e-cli-en-go)
5. [Variables de Entorno y Opciones de Configuración](#5-variables-de-entorno-y-opciones-de-configuración)
6. [Solución de Problemas Frecuentes (FAQ / Troubleshooting)](#6-solución-de-problemas-frecuentes-faq--troubleshooting)

---

## 1. Requisitos Mínimos

Dependiendo de cómo decidas ejecutarlo:

| Método | Requisitos |
| :--- | :--- |
| **Nativo (Python)** | Python 3.10 o superior (marcar *"Add python.exe to PATH"* durante la instalación). |
| **Docker** | Docker Desktop (Windows / Mac) o Docker Engine + Compose (Linux). |
| **Orquestador Go** | Go 1.22+ (solo si deseas compilar los binarios de la carpeta `go_app/`). |

---

## 2. Instalación Rápida Paso a Paso (PC limpia)

### Opción 1: Instalación Standalone en Windows (Recomendada para uso nativo)

Si estás en Windows y acabas de clonar el proyecto, existe un script automatizado que realiza toda la instalación en 1 solo clic:

1. Asegúrate de tener **Python 3.10+** instalado y agregado al PATH.
2. Haz doble clic en el archivo:
   ```cmd
   setup_standalone.bat
   ```
   *(o ejecútalo desde PowerShell/CMD en la carpeta raíz del proyecto)*.
3. El script automáticamente:
   - Verificará la versión de Python.
   - Creará el entorno virtual `.venv`.
   - Instalará todas las librerías necesarias (`camoufox[geoip]`, `playwright`, etc.).
   - Descargará el navegador anti-detección Camoufox (`python -m camoufox fetch`).
   - Compilará las herramientas de Go si Go está presente.

---

### Opción 2: Instalación Manual con Python

Si prefieres realizar el proceso comando por comando o estás en Linux/macOS:

#### Paso 1: Abrir la terminal en la raíz del repositorio
```bash
cd CamouMacro
```

#### Paso 2: Crear y activar un entorno virtual
- **En Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
  *(Si PowerShell bloquea la ejecución de scripts, ejecuta primero: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **En Windows (CMD):**
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate.bat
  ```

- **En Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

#### Paso 3: Instalar dependencias requeridas
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Paso 4: Descargar los binarios del navegador Camoufox
Camoufox utiliza un motor basado en Firefox con parches anti-huella digital C++. Debes descargar sus binarios una sola vez:
```bash
python -m camoufox fetch
```

#### Paso 5 (Opcional): Instalar navegadores Playwright
Si deseas utilizar módulos auxiliares de Chromium:
```bash
playwright install chromium
```

---

### Opción 3: Despliegue con Docker (Cero dependencias)

Si no quieres instalar Python ni configurar entornos locales:

1. Abre **Docker Desktop**.
2. En la raíz de CamouMacro:
   - **En Windows:** Haz doble clic en `run_docker.bat` o escribe:
     ```powershell
     docker compose up
     ```
   - **En Linux:**
     ```bash
     chmod +x run_docker.sh
     ./run_docker.sh
     ```
Docker se encargará de compilar el orquestador, configurar Tor, descargar Camoufox y ejecutar el algoritmo en segundo plano.

---

## 3. Configuración de Objetivos y Género (profiles_dict.txt)

El archivo de configuración principal de objetivos se encuentra en:
- `targets/profiles_dict.txt` (y se replica en `python_engine/targets/profiles_dict.txt`).

### Estructura del Archivo

```json
{
  "target_gender": "men",
  "account_gender": "women",
  "targets": {
    "Enrique": 40
  }
}
```

### Campos disponibles:
- **`target_gender`**: El género de las personas que deseas buscar e interactuar en la plataforma.
  - Opciones: `"men"` (para buscar hombres) o `"women"` (para buscar mujeres).
- **`account_gender`**: El género del perfil que el bot creará automáticamente.
  - Opciones: `"women"`, `"men"` o `"auto"`.
  - Si se deja en `"auto"` o no se especifica, el algoritmo seleccionará automáticamente el género opuesto a `target_gender`.
- **`targets`**: Diccionario con el nombre del objetivo como clave y su edad como valor entero. El bot escaneará las tarjetas y sólo interactuará cuando coincidan el nombre y la edad.

### Ejemplo para buscar mujeres con cuenta masculina:
```json
{
  "target_gender": "women",
  "account_gender": "men",
  "targets": {
    "Anna": 46,
    "Zol": 41,
    "Kathe": 34
  }
}
```

---

## 4. Cómo Abrir y Ejecutar el Algoritmo (Formas de Inicio)

CamouMacro ofrece múltiples interfaces según la necesidad de uso:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FORMAS DE EJECUCIÓN                             │
├────────────────────────────┬─────────────────────────────┬─────────────┤
│ Interfaz                   │ Comando                     │ Ideal para  │
├────────────────────────────┼─────────────────────────────┼─────────────┤
│ 1. Panel Gráfico (GUI)     │ python camoumacro.py        │ Control visual, multiventana │
│ 2. Menú Interactivo        │ python main.py              │ Terminal interactiva directa │
│ 3. CLI Runner              │ python python_engine/runner.py │ Automatización/Scripts    │
│ 4. Dashboard TUI (Go)      │ .\go_app\bin\camoumacro-tui.exe │ Rendimiento nativo      │
│ 5. Contenedor Docker       │ docker compose up           │ Servidores / VPS           │
└────────────────────────────┴─────────────────────────────┴─────────────┘
```

---

### Método A: Panel de Control de Escritorio (GUI Tkinter)

Es la forma más visual, intuitiva y recomendada para gestionar instancias.

```powershell
python camoumacro.py
```

#### Controles disponibles en la ventana:
- **Configuración de Tiempos**: Permite ajustar `Speed Factor`, `Cooldown entre mensajes`, `Cantidad de stickers`, etc.
- **Selectores de Género**:
  - **Género Objetivo**: Permite elegir entre `women` o `men`.
  - **Género Cuenta**: Permite elegir entre `auto`, `men` o `women`.
- **Selector de Algoritmo**: Escoge entre `allfeellove_auto` o `form_demo`.
- **Modo Headless**: Casilla para ver el navegador abriéndose en pantalla o ejecutarlo oculto.
- **Botón `💾 Guardar Config`**: Persiste los ajustes en `config/settings.py`.
- **Botón `＋ Lanzar Nueva Instancia`**: Abre una nueva consola independiente con su propio puerto Tor asignado, ejecutando el algoritmo en paralelo.

---

### Método B: Menú Interactivo en Terminal (main.py)

Ideal para iniciar rápidamente desde cualquier consola:

```powershell
python main.py
```

1. Aparecerá un menú interactivo en la terminal con colores ANSI.
2. Usa las flechas o introduce el número de la opción deseada:
   - `[1] Formulario de prueba (demo)`
   - `[2] Allfeellove Auto`
   - `[3] Salir`
3. El proceso iniciará automáticamente el servicio de Tor en segundo plano (puerto `9050` o siguiente libre), inicializará Camoufox y correrá el ciclo de vida.
4. Al terminar o reiniciarse, rotará automáticamente de identidad y proxy.

---

### Método C: Ejecución por Consola con Parámetros (runner.py)

Permite ejecutar el motor directamente especificando opciones por argumentos CLI:

```powershell
python python_engine/runner.py --algo allfeellove_auto --target-gender men --account-gender women --tor-port 9050
```

#### Parámetros disponibles:
- `--algo [nombre]`: Algoritmo a ejecutar (`allfeellove_auto`, `form_demo`).
- `--target-gender [women|men]`: Género a buscar.
- `--account-gender [auto|men|women]`: Género de la cuenta a registrar.
- `--tor-port [puerto]`: Puerto del proxy SOCKS5 de Tor (por defecto `9050`).
- `--headless`: Ejecuta el navegador sin interfaz gráfica.
- `--speed-factor [flotante]`: Multiplicador de esperas (`1.0` = normal, `0.5` = doble de rápido).
- `--width [px]` y `--height [px]`: Dimensiones de la ventana del navegador.
- `--list-algos`: Lista los algoritmos disponibles y sale.

---

### Método D: Dashboard Interactivo en Go (TUI Bubbletea)

Si compilaste los ejecutables con `setup_standalone.bat` o tienes Go instalado:

```powershell
.\go_app\bin\camoumacro-tui.exe
```

#### Atajos de Teclado del Dashboard:
- `[s]` o `[Enter]`: Iniciar el orquestador y los workers.
- `[x]`: Detener la ejecución actual.
- `[Tab]`: Cambiar el algoritmo seleccionado.
- `[h]`: Alternar modo Headless (oculto / visible).
- `[l]`: Activar o desactivar el bucle continuo con rotación de identidad.
- `[+]` / `[-]`: Subir o bajar la velocidad de interacción.
- `[q]` o `[Ctrl+C]`: Salir del programa.

---

### Método E: CLI en Go

Para entornos sin interfaz gráfica o tareas programadas de Windows / Cron en Linux:

```powershell
.\go_app\bin\camoumacro-cli.exe -algo allfeellove_auto -headless=false -loop=true
```

---

## 5. Variables de Entorno y Opciones de Configuración

Puedes crear un archivo `.env` en la raíz del proyecto (basado en `.env.example`) o configurar variables del sistema para controlar el comportamiento:

```bash
# Algoritmo
ALGO=allfeellove_auto

# Control de Género
TARGET_GENDER=men       # "men" o "women"
ACCOUNT_GENDER=women    # "women", "men" o "auto"

# Navegador y Red
HEADLESS=false          # true para modo oculto, false para ver el navegador
TOR_PORT=9050           # Puerto inicial de Tor SOCKS5
SPEED_FACTOR=1.0        # 0.5 (rápido), 1.0 (normal), 1.5 (humano pausado)

# Archivo de perfiles objetivo
TARGETS_FILE=targets/profiles_dict.txt

# Límites del algoritmo
MAX_SCAN_PAGES=100
MESSAGE_COOLDOWN_SECONDS=2.5
STICKER_COUNT=5
STICKER_INTERVAL_MS=400
```

---

## 6. Solución de Problemas Frecuentes (FAQ / Troubleshooting)

### 1. `python no se reconoce como un comando interno o externo`
- **Causa**: Python no fue añadido a las variables de entorno del sistema al instalarse.
- **Solución**: Vuelve a ejecutar el instalador de Python oficial, selecciona **Modify**, y marca la casilla **"Add Python to PATH"**.

### 2. Error de políticas de ejecución de scripts en PowerShell
- **Mensaje**: `No se puede cargar el archivo Activate.ps1 porque la ejecución de scripts está deshabilitada en este sistema.`
- **Solución**: Abre PowerShell y ejecuta:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
  Luego vuelve a activar el entorno virtual con `.\.venv\Scripts\Activate.ps1`.

### 3. Falta de binarios de Camoufox
- **Mensaje**: `Camoufox browser binary not found` o error al instanciar el driver.
- **Solución**: Ejecuta en la terminal con el entorno virtual activo:
  ```powershell
  python -m camoufox fetch
  ```

### 4. Bloqueo de Cloudflare o problemas de conexión
- **Causa**: La IP de salida está bloqueada o la red presenta congestión.
- **Comportamiento**: El algoritmo detecta automáticamente bloqueos de Cloudflare y ejecuta `driver.rotate_connection()`, reiniciando el circuito de Tor para obtener una IP limpia.
- **Verificación**: Asegúrate de que Tor tenga acceso a internet en tu cortafuegos/firewall. Si usas Tor Browser de escritorio, asegúrate de que el puerto SOCKS5 coincida con el configurado (generalmente `9050` o `9150`).

### 5. ¿Cómo cambiar los mensajes que se envían?
- Los mensajes están centralizados en `modules/InfoGeneration/peopleTalk_generator.py`.
- Puedes editar o agregar nuevos tonos (`flirty`, `casual`, `premium`) tanto para hombres como para mujeres en `TONES_BY_GENDER`.
