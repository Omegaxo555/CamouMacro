# CamouMacro Hybrid Suite

**CamouMacro** es una suite de automatización web avanzada y anónima que combina lo mejor de dos mundos:
- **Go 1.24**: Orquestador de alto rendimiento, gestión del ciclo de vida de procesos, control de la red **Tor** y dashboards interactivos (TUI con Bubbletea y GUI con Fyne v2).
- **Python + Camoufox**: Motor de evasión anti-detección y anti-fingerprinting con Firefox integrado para eludir bloqueos como Cloudflare.

---

## 🚀 Despliegue Rápido (Zero Dependencies)

No necesitas instalar Python, Go ni configurar nada en la máquina destino si usas **Docker**.

### Opción A: Despliegue con Docker (Cualquier Sistema Operativo)

1. Clona el repositorio en la máquina destino:
   ```bash
   git clone https://github.com/omegaxo555/camoumacro.git
   cd camoumacro
   ```

2. Ejecuta con 1 solo comando:
   - **En Windows**: Doble clic en `run_docker.bat` o ejecuta:
     ```powershell
     docker compose up
     ```
   - **En Linux / VPS**:
     ```bash
     chmod +x run_docker.sh
     ./run_docker.sh
     ```

3. **Configuración de Variables (Opcional)**:
   Puedes crear un archivo `.env` (basado en `.env.example`) para cambiar opciones:
   ```env
   ALGO=allfeellove_auto
   HEADLESS=true
   SPEED_FACTOR=1.0
   TOR_PORT=9050
   ```

---

## 💻 Despliegue Standalone (Nativo en Windows sin Docker)

Si prefieres ejecutar directamente en Windows sin contenedor:

1. **Instalación automática en 1 clic**:
   Ejecuta `setup_standalone.bat`. Creará el entorno `.venv`, instalará los paquetes y compilará los ejecutables de Go.

2. **Ejecutar el Dashboard Interactivo (TUI)**:
   ```powershell
   .\go_app\bin\camoumacro-tui.exe
   ```
   **Controles del Dashboard:**
   - `[s]` / `[Enter]`: Iniciar automatización
   - `[x]`: Detener
   - `[Tab]`: Cambiar algoritmo
   - `[h]`: Activar / Desactivar modo Headless
   - `[l]`: Activar / Desactivar reinicio tras éxito o error (con rotación Tor; OFF deja abierto el navegador)
   - `[a]`: Activar / Desactivar filtro `ALL` (incluye inactivos; OFF conserva `ONLY ACTIVE`)
   - `[m]`: Alternar entre 1, 2 y 3 macros concurrentes, cada una con Tor independiente
   - `[+]` / `[-]`: Ajustar velocidad de ejecución
   - `[q]`: Salir

3. **Ejecutar en modo CLI rápido**:
   ```powershell
   .\go_app\bin\camoumacro-cli.exe -algo allfeellove_auto -macros 2 -headless=true -loop=false -all-users=true
   ```

---

## 📁 Estructura del Proyecto

```
CamouMacro/
├── Dockerfile                   # Imagen multi-stage (Go Builder + Python/Tor Runtime)
├── docker-compose.yml           # Configuración de 1-comando
├── run_docker.bat               # Launcher 1-clic para Windows Docker
├── run_docker.sh                # Launcher 1-clic para Linux Docker
├── setup_standalone.bat         # Instalador 1-clic nativo Windows
│
├── go_app/                      # [GO] Orquestador, Tor Manager y UIs
│   ├── bin/
│   │   ├── camoumacro-tui.exe   # Dashboard interactivo con Bubbletea
│   │   └── camoumacro-cli.exe   # Orquestador por línea de comandos
│   ├── cmd/                     # Puntos de entrada (tui, cli, gui)
│   ├── internal/                # tor, orchestrator, ui, config
│   └── go.mod
│
└── python_engine/               # [PYTHON] Motor de Browser Camoufox
    ├── core/                    # camoufox_handler (anti-fingerprint)
    ├── modules/                 # allfeellove_auto, form_automator, etc.
    ├── runner.py                # Entrypoint CLI/IPC
    └── requirements.txt
```
