"""Runner CLI para el motor de automatización Camoufox.

Permite invocar cualquier algoritmo con parámetros explícitos pasados por el orquestador en Go.
Este archivo es el único componente dentro de python_engine/; todos los módulos reutilizables
(core/, modules/, config/, targets/, templates/) residen en el directorio raíz del proyecto.
"""

import argparse
import os
import sys
import traceback
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Resolución de rutas: este script vive en <root>/python_engine/runner.py
# Los módulos compartidos están en <root>/ (directorio padre).
# ─────────────────────────────────────────────────────────────────────────────
RUNNER_DIR = Path(__file__).resolve().parent   # <root>/python_engine/
PROJECT_ROOT = RUNNER_DIR.parent               # <root>/

# Insertar la raíz del proyecto al frente del sys.path para que
# "from core.xxx import ...", "from modules.xxx import ...", etc. funcionen
# sin duplicar ningún archivo dentro de python_engine/.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.camoufox_handler import CamoufoxHandler
from core.window_layout import get_tiled_window_layout
from modules.allfeellove_auto import run_allfeellove_auto
from modules.form_automator import FormAutomator
from modules.InfoGeneration.peopleInfo_generator import PeopleInfoGenerator


def run_form_demo(driver: CamoufoxHandler) -> None:
    """Demostración del módulo FormAutomator con generación adaptable."""
    print("[runner] Ejecutando formulario de prueba...")
    if not driver.navigate("https://httpbin.org/forms/post"):
        print("[runner] [ERROR] No se pudo abrir la URL de prueba.")
        sys.exit(1)

    gender = os.getenv("ACCOUNT_GENDER", "random")
    profile = PeopleInfoGenerator.generate_profile(gender=gender)
    print(f"[runner] Identidad generada: {profile['name']} ({profile['gender']})")

    automator = FormAutomator(driver.page)
    automator.human_type("input[name='custname']", profile["name"])
    automator.human_type("input[name='custemail']", profile["email"])
    automator.human_type("textarea[name='comments']", f"Prueba automatizada desde CamouMacro ({profile['gender']})")
    print(f"[runner] [OK] Formulario completado con éxito para {profile['name']}.")


ALGORITHMS = {
    "form_demo": run_form_demo,
    "allfeellove_auto": run_allfeellove_auto,
}


def parse_args():
    parser = argparse.ArgumentParser(description="CamouMacro Python Automation Engine")
    parser.add_argument("--algo", type=str, default="allfeellove_auto", help="ID del algoritmo a ejecutar")
    parser.add_argument("--tor-port", type=int, default=9050, help="Puerto del proxy SOCKS5 Tor")
    parser.add_argument(
        "--tor-ports",
        type=lambda value: [int(port) for port in value.split(",")],
        default=None,
        help="Puertos SOCKS5 permitidos para esta macro, separados por comas",
    )
    parser.add_argument("--headless", action="store_true", help="Ejecutar navegador en modo headless")
    parser.add_argument("--speed-factor", type=float, default=1.0, help="Multiplicador de velocidad de delays")
    parser.add_argument("--template", type=str, default="templates/perfil_base.tar.gz", help="Plantilla de perfil")
    parser.add_argument("--width", type=int, default=560, help="Ancho de ventana")
    parser.add_argument("--height", type=int, default=420, help="Alto de ventana")
    parser.add_argument("--macro-index", type=int, default=0, help="Índice de esta macro para colocar su ventana")
    parser.add_argument("--macro-count", type=int, default=1, help="Cantidad total de macros concurrentes")
    parser.add_argument("--target-gender", type=str, default=None, choices=["women", "men"], help="Género del objetivo a buscar")
    parser.add_argument("--account-gender", type=str, default=None, choices=["men", "women", "auto"], help="Género del perfil a crear")
    parser.add_argument("--keep-open", action="store_true", help="Esperar a que el usuario cierre el navegador al terminar")
    parser.add_argument("--list-algos", action="store_true", help="Listar algoritmos soportados y salir")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.list_algos:
        for k in ALGORITHMS.keys():
            print(k)
        return

    if args.algo not in ALGORITHMS:
        print(f"[runner] [ERROR] Algoritmo desconocido: '{args.algo}'. Opciones válidas: {list(ALGORITHMS.keys())}")
        sys.exit(1)
    if args.macro_count < 1 or args.macro_count > 6:
        print("[runner] [ERROR] La cantidad de macros debe estar entre 1 y 6.")
        sys.exit(2)
    if not 0 <= args.macro_index < args.macro_count:
        print("[runner] [ERROR] El índice de macro debe estar entre 0 y macro-count - 1.")
        sys.exit(2)

    # Inyectar variables de entorno para que los settings.py las tomen
    os.environ["SPEED_FACTOR"] = str(args.speed_factor)
    os.environ["HEADLESS"] = str(args.headless).lower()
    os.environ["TOR_PORT"] = str(args.tor_port)
    if args.target_gender:
        os.environ["TARGET_GENDER"] = args.target_gender
    if args.account_gender:
        os.environ["ACCOUNT_GENDER"] = args.account_gender

    # Resolver la plantilla de perfil relativa a la raíz del proyecto
    template_path = PROJECT_ROOT / args.template
    template_str = str(template_path) if template_path.is_file() else None

    print(f"[runner] Raíz del proyecto: {PROJECT_ROOT}")
    print(f"[runner] Inicializando Camoufox en Tor proxy socks5://127.0.0.1:{args.tor_port} (Headless: {args.headless})...")

    tor_ports = args.tor_ports or [args.tor_port]
    if not tor_ports or any(port < 1 or port > 65535 for port in tor_ports):
        print("[runner] [ERROR] La lista de puertos Tor contiene valores fuera de rango.")
        sys.exit(2)

    window_size = (args.width, args.height)
    window_position = None
    if not args.headless and args.macro_count > 1:
        try:
            window_position, window_size = get_tiled_window_layout(
                window_size,
                args.macro_index,
                args.macro_count,
            )
            print(
                f"[runner] Ventana de macro {args.macro_index + 1}/{args.macro_count}: "
                f"{window_size[0]}x{window_size[1]} en {window_position[0]},{window_position[1]}."
            )
        except OSError as exc:
            print(f"[runner] [WARN] No se pudo calcular el mosaico de ventanas: {exc}")

    driver = CamoufoxHandler(
        tor_proxy=f"socks5://127.0.0.1:{args.tor_port}",
        tor_ports=tor_ports,
        profile_template=template_str,
        headless=args.headless,
        window_size=window_size,
        window_position=window_position,
    )

    try:
        if not driver.initialize():
            print("[runner] [FATAL] Error al inicializar el navegador Camoufox.")
            sys.exit(2)

        print(f"[runner] Ejecutando algoritmo '{args.algo}'...")
        handler_fn = ALGORITHMS[args.algo]
        handler_fn(driver)
        print(f"[runner] [SUCCESS] Algoritmo '{args.algo}' finalizado exitosamente.")
    except Exception as exc:
        print(f"[runner] [ERROR] Excepción durante la ejecución: {exc}")
        traceback.print_exc()
        sys.exit(3)
    finally:
        try:
            if args.keep_open:
                driver.wait_until_closed()
        finally:
            print("[runner] Limpiando recursos y cerrando navegador...")
            driver.close()


if __name__ == "__main__":
    main()
