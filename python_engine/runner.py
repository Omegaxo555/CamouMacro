"""Runner CLI para el motor de automatización Camoufox.

Permite invocar cualquier algoritmo con parámetros explícitos pasados por el orquestador en Go.
"""

import argparse
import os
import sys
import traceback
from pathlib import Path

# Añadir directorio actual al PATH de Python
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from core.camoufox_handler import CamoufoxHandler
from modules.allfeellove_auto import run_allfeellove_auto
from modules.form_automator import FormAutomator


def run_form_demo(driver: CamoufoxHandler) -> None:
    """Demostración del módulo FormAutomator."""
    print("[runner] Ejecutando formulario de prueba...")
    if not driver.navigate("https://httpbin.org/forms/post"):
        print("[runner] [ERROR] No se pudo abrir la URL de prueba.")
        sys.exit(1)

    automator = FormAutomator(driver.page)
    automator.human_type("input[name='custname']", "Alex Ruiz")
    automator.human_type("input[name='custemail']", "alex@example.com")
    automator.human_type("textarea[name='comments']", "Prueba automatizada desde CamouMacro (Go+Python Hybrid)")
    print("[runner] [OK] Formulario completado con éxito.")


ALGORITHMS = {
    "form_demo": run_form_demo,
    "allfeellove_auto": run_allfeellove_auto,
}


def parse_args():
    parser = argparse.ArgumentParser(description="CamouMacro Python Automation Engine")
    parser.add_argument("--algo", type=str, default="allfeellove_auto", help="ID del algoritmo a ejecutar")
    parser.add_argument("--tor-port", type=int, default=9050, help="Puerto del proxy SOCKS5 Tor")
    parser.add_argument("--headless", action="store_true", help="Ejecutar navegador en modo headless")
    parser.add_argument("--speed-factor", type=float, default=1.0, help="Multiplicador de velocidad de delays")
    parser.add_argument("--template", type=str, default="templates/perfil_base.tar.gz", help="Plantilla de perfil")
    parser.add_argument("--width", type=int, default=560, help="Ancho de ventana")
    parser.add_argument("--height", type=int, default=420, help="Alto de ventana")
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

    # Inyectar variables de entorno para que los settings.py las tomen
    os.environ["SPEED_FACTOR"] = str(args.speed_factor)
    os.environ["HEADLESS"] = str(args.headless).lower()
    os.environ["TOR_PORT"] = str(args.tor_port)

    template_path = CURRENT_DIR / args.template
    template_str = str(template_path) if template_path.is_file() else None

    print(f"[runner] Inicializando Camoufox en Tor proxy socks5://127.0.0.1:{args.tor_port} (Headless: {args.headless})...")
    
    driver = CamoufoxHandler(
        tor_proxy=f"socks5://127.0.0.1:{args.tor_port}",
        profile_template=template_str,
        headless=args.headless,
        window_size=(args.width, args.height),
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
        print("[runner] Limpiando recursos y cerrando navegador...")
        driver.close()


if __name__ == "__main__":
    main()
