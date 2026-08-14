"""Aplicación principal con menú interactivo de selección de algoritmos."""

import os
import sys

from core.camoufox_handler import CamoufoxHandler
from modules.custom_algorithm import run_custom_algorithm
from modules.form_automator import FormAutomator


ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "fg_cyan": "\033[36m",
    "fg_yellow": "\033[33m",
    "fg_green": "\033[32m",
    "fg_red": "\033[31m",
    "bg_blue": "\033[44m",
    "bg_gray": "\033[100m",
}


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def press_any_key() -> None:
    if os.name == "nt":
        os.system("pause > nul")
    else:
        input("\nPresiona Enter para continuar...")


def run_form_demo(driver: CamoufoxHandler) -> None:
    """Demostración del módulo FormAutomator."""
    print(f"{ANSI['fg_cyan']}[demo]{ANSI['reset']} Ejecutando formulario de prueba...")
    if not driver.navigate("https://httpbin.org/forms/post"):
        print(f"{ANSI['fg_red']}[-] No se pudo abrir la URL de prueba.{ANSI['reset']}")
        return

    automator = FormAutomator(driver.page)
    automator.human_type("input[name='custname']", "Alex Ruiz")
    automator.human_type("input[name='custemail']", "alex@example.com")
    automator.human_type("textarea[name='comments']", "Prueba automatizada desde CamouMacro")
    print(f"{ANSI['fg_green']}[ok]{ANSI['reset']} Formulario completado.")


def run_exit() -> None:
    print(f"{ANSI['fg_yellow']}Saliendo del menú...{ANSI['reset']}")


ALGORITHMS = [
    {"id": "form_demo", "label": "Formulario de prueba", "handler": run_form_demo},
    {"id": "custom_algorithm", "label": "Mi algoritmo personalizado", "handler": run_custom_algorithm},
    {"id": "exit", "label": "Salir", "handler": run_exit},
]


def show_algorithm_menu() -> dict:
    index = 0
    while True:
        clear_screen()
        print(f"{ANSI['bold']}=== CamouMacro - Selección de algoritmo ==={ANSI['reset']}")
        print(f"{ANSI['dim']}Usa ↑ ↓ para moverte y Enter para confirmar.{ANSI['reset']}\n")

        for i, option in enumerate(ALGORITHMS):
            prefix = " > " if i == index else "   "
            color = ANSI["bg_blue"] if i == index else ANSI["bg_gray"]
            print(f"{color}{prefix}{option['label']}{ANSI['reset']}")

        key = input("\nSelecciona una opción: ").strip().lower()

        if key in {"w", "up", "8"}:
            index = (index - 1) % len(ALGORITHMS)
            continue
        if key in {"s", "down", "2"}:
            index = (index + 1) % len(ALGORITHMS)
            continue
        if key in {"", "enter", "\n"}:
            return ALGORITHMS[index]

        if key.isdigit() and 1 <= int(key) <= len(ALGORITHMS):
            return ALGORITHMS[int(key) - 1]

        print(f"{ANSI['fg_red']}Opción inválida. Intenta con ↑ ↓ o un número.{ANSI['reset']}")
        press_any_key()


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
            print(f"{ANSI['fg_red']}[-] Error al inicializar el driver.{ANSI['reset']}")
            return

        while True:
            selected = show_algorithm_menu()
            option_id = selected["id"]

            if option_id == "exit":
                selected["handler"]()
                break

            selected["handler"](driver)
            print(f"\n{ANSI['fg_yellow']}¿Quieres ejecutar otro algoritmo?{ANSI['reset']}")
            again = input("[s/n]: ").strip().lower()
            if again not in {"s", "si", "y", "yes"}:
                print("Saliendo del menú.")
                break

    finally:
        driver.close()


if __name__ == "__main__":
    main()