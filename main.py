"""Aplicación principal con menú interactivo de selección de algoritmos."""

import os
import shutil
import socket
import subprocess
import sys
import time
import traceback
from pathlib import Path

from core.camoufox_handler import CamoufoxHandler
from core.terminal_ui import TerminalUI
from modules.allfeellove_auto import run_allfeellove_auto
from modules.form_automator import FormAutomator

TOR_PROCESS = None


def is_port_open(host: str = "127.0.0.1", port: int = 9050, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def find_tor_executable() -> str | None:
    candidates = []

    if os.name == "nt":
        candidates.extend([
            "tor.exe",
            shutil.which("tor.exe"),
            r"C:\Users\paulo\AppData\Local\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
            r"C:\Program Files\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
            r"C:\Program Files (x86)\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
        ])
    else:
        candidates.extend([
            "tor",
            shutil.which("tor"),
            "/usr/bin/tor",
            "/usr/local/bin/tor",
        ])

    for candidate in candidates:
        if not candidate:
            continue
        if os.path.exists(candidate):
            return str(candidate)
        if shutil.which(candidate):
            return shutil.which(candidate)
    return None


def start_tor_background(port: int = 9050) -> subprocess.Popen | None:
    global TOR_PROCESS

    if is_port_open(port=port):
        print(f"{TerminalUI.ANSI['fg_green']}[tor]{TerminalUI.ANSI['reset']} Tor ya está corriendo en 127.0.0.1:{port}")
        return None

    tor_path = find_tor_executable()
    if not tor_path:
        print(f"{TerminalUI.ANSI['fg_red']}[tor]{TerminalUI.ANSI['reset']} No se encontró 'tor' ni 'tor.exe' en el sistema.")
        return None

    try:
        if os.name == "nt":
            TOR_PROCESS = subprocess.Popen(
                [tor_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=str(Path(tor_path).parent),
            )
        else:
            TOR_PROCESS = subprocess.Popen(
                [tor_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

        for _ in range(30):
            if is_port_open(port=port):
                print(f"{TerminalUI.ANSI['fg_green']}[tor]{TerminalUI.ANSI['reset']} Tor arrancó correctamente en 127.0.0.1:{port}")
                return TOR_PROCESS
            time.sleep(0.5)

        print(f"{TerminalUI.ANSI['fg_red']}[tor]{TerminalUI.ANSI['reset']} Tor se inició pero no respondió en 127.0.0.1:{port}.")
        stop_tor_background()
        return None
    except Exception as exc:
        print(f"{TerminalUI.ANSI['fg_red']}[tor]{TerminalUI.ANSI['reset']} Error al iniciar Tor: {exc}")
        return None


def stop_tor_background() -> None:
    global TOR_PROCESS

    if TOR_PROCESS is None:
        return

    try:
        if TOR_PROCESS.poll() is None:
            if os.name == "nt":
                TOR_PROCESS.terminate()
            else:
                TOR_PROCESS.terminate()
            try:
                TOR_PROCESS.wait(timeout=10)
            except subprocess.TimeoutExpired:
                TOR_PROCESS.kill()
                TOR_PROCESS.wait(timeout=10)
        print(f"{TerminalUI.ANSI['fg_yellow']}[tor]{TerminalUI.ANSI['reset']} Tor detenido.")
    except Exception as exc:
        print(f"{TerminalUI.ANSI['fg_red']}[tor]{TerminalUI.ANSI['reset']} Error cerrando Tor: {exc}")
    finally:
        TOR_PROCESS = None


def run_form_demo(driver: CamoufoxHandler) -> None:
    """Demostración del módulo FormAutomator."""
    print(f"{TerminalUI.ANSI['fg_cyan']}[demo]{TerminalUI.ANSI['reset']} Ejecutando formulario de prueba...")
    if not driver.navigate("https://httpbin.org/forms/post"):
        print(f"{TerminalUI.ANSI['fg_red']}[-] No se pudo abrir la URL de prueba.{TerminalUI.ANSI['reset']}")
        return

    automator = FormAutomator(driver.page)
    automator.human_type("input[name='custname']", "Alex Ruiz")
    automator.human_type("input[name='custemail']", "alex@example.com")
    automator.human_type("textarea[name='comments']", "Prueba automatizada desde CamouMacro")
    print(f"{TerminalUI.ANSI['fg_green']}[ok]{TerminalUI.ANSI['reset']} Formulario completado.")


def run_exit() -> None:
    print(f"{TerminalUI.ANSI['fg_yellow']}Saliendo del menú...{TerminalUI.ANSI['reset']}")


def build_driver_for_port(port: int = 9050) -> CamoufoxHandler:
    return CamoufoxHandler(
        tor_proxy=f"socks5://127.0.0.1:{port}",
        profile_template="templates/perfil_base.tar.gz",
        headless=False,
        window_size=(600, 800),
    )


ALGORITHMS = [
    {"id": "form_demo", "label": "Formulario de prueba", "handler": run_form_demo},
    {"id": "allfeellove_auto", "label": "Allfeellove Auto", "handler": run_allfeellove_auto},
    {"id": "exit", "label": "Salir", "handler": run_exit},
]


def show_algorithm_menu() -> dict:
    options = [item["label"] for item in ALGORITHMS]
    selected_index = TerminalUI.select_option("=== CamouMacro - Selección de algoritmo ===", options)
    return ALGORITHMS[selected_index]


def run_algorithm_with_debug(driver: CamoufoxHandler, selected: dict) -> None:
    option_id = selected["id"]
    print(f"\n{TerminalUI.ANSI['fg_cyan']}[debug] Iniciando algoritmo: {option_id}{TerminalUI.ANSI['reset']}")
    try:
        selected["handler"](driver)
        print(f"{TerminalUI.ANSI['fg_green']}[debug] Finalizó el algoritmo: {option_id}{TerminalUI.ANSI['reset']}")
    except Exception as exc:
        print(f"{TerminalUI.ANSI['fg_red']}[debug] ERROR en algoritmo: {option_id}{TerminalUI.ANSI['reset']}")
        print(f"{TerminalUI.ANSI['fg_red']}[debug] Excepción: {exc}{TerminalUI.ANSI['reset']}")
        traceback.print_exc()
        if driver.page is not None:
            print(f"{TerminalUI.ANSI['fg_yellow']}[debug] URL actual: {driver.page.url}{TerminalUI.ANSI['reset']}")
        print(f"{TerminalUI.ANSI['fg_yellow']}[debug] Presiona Enter para volver al menú...{TerminalUI.ANSI['reset']}")
        input()


def main():
    current_port = 9050
    start_tor_background(port=current_port)

    driver = build_driver_for_port(current_port)

    try:
        if not driver.initialize():
            print(f"{TerminalUI.ANSI['fg_red']}[-] Error al inicializar el driver.{TerminalUI.ANSI['reset']}")
            return

        while True:
            selected = show_algorithm_menu()
            option_id = selected["id"]

            if option_id == "exit":
                selected["handler"]()
                break

            run_algorithm_with_debug(driver, selected)

            repeat_current = input("¿Quieres repetir este mismo algoritmo? (S/N) [N]: ").strip().lower()
            if repeat_current in ("", "s", "si", "y", "yes"):
                print(f"{TerminalUI.ANSI['fg_yellow']}[restart]{TerminalUI.ANSI['reset']} Reiniciando navegador y Tor para repetir el algoritmo...")
                driver.close()
                stop_tor_background()
                current_port = 9051 if current_port == 9050 else 9050
                if not start_tor_background(port=current_port):
                    print(f"{TerminalUI.ANSI['fg_red']}[restart]{TerminalUI.ANSI['reset']} No se pudo arrancar Tor en el puerto {current_port}.")
                    break
                driver = build_driver_for_port(current_port)
                if not driver.initialize():
                    print(f"{TerminalUI.ANSI['fg_red']}[restart]{TerminalUI.ANSI['reset']} Error al reinicializar el navegador.")
                    break
                continue

            again = input("¿Quieres ejecutar otro algoritmo? (S/N) [S]: ").strip().lower()
            if again in ("", "s", "si", "y", "yes"):
                continue
            print("Saliendo del menú.")
            break

    finally:
        driver.close()
        stop_tor_background()


if __name__ == "__main__":
    main()