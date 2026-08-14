"""Aplicación principal con menú interactivo de selección de algoritmos."""

import traceback

from core.camoufox_handler import CamoufoxHandler
from core.terminal_ui import TerminalUI
from modules.allfeellove_auto import run_allfeellove_auto
from modules.form_automator import FormAutomator


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
    plantilla_perfil = "templates/perfil_base.tar.gz"

    driver = CamoufoxHandler(
        tor_proxy="socks5://127.0.0.1:9050",
        profile_template=plantilla_perfil,
        headless=False,
        window_size=(400, 600),
    )

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
            again = TerminalUI.confirm("¿Quieres ejecutar otro algoritmo?", default=True)
            if not again:
                print("Saliendo del menú.")
                break

    finally:
        driver.close()


if __name__ == "__main__":
    main()