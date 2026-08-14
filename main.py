"""Aplicación principal con menú de selección de algoritmos."""

from core.camoufox_handler import CamoufoxHandler
from modules.form_automator import FormAutomator


def run_form_demo(driver: CamoufoxHandler) -> None:
    """Demostración del módulo FormAutomator."""
    if not driver.navigate("https://httpbin.org/forms/post"):
        print("[-] No se pudo abrir la URL de prueba.")
        return

    automator = FormAutomator(driver.page)
    automator.human_type("input[name='custname']", "Alex Ruiz")
    automator.human_type("input[name='custemail']", "alex@example.com")
    automator.human_type("textarea[name='comments']", "Prueba automatizada desde CamouMacro")


def run_exit() -> None:
    print("Saliendo del menú...")


ALGORITHMS = {
    "1": ("form_demo", run_form_demo, "Formulario de prueba con FormAutomator"),
    "2": ("exit", run_exit, "Salir"),
}


def show_algorithm_menu() -> str:
    print("\n=== Selección de algoritmo ===")
    for key, (_, _, description) in ALGORITHMS.items():
        print(f"  [{key}] {description}")

    while True:
        choice = input("Elegir algoritmo (1-2): ").strip()
        if choice in ALGORITHMS:
            return choice
        print("Opción inválida. Intenta otra vez.")


def main():
    plantilla_perfil = "templates/perfil_base.tar.gz"

    driver = CamoufoxHandler(
        tor_proxy="socks5://127.0.0.1:9050",
        profile_template=plantilla_perfil,
        headless=False,
        window_size=(600, 900),
    )

    try:
        if not driver.initialize():
            print("[-] Error al inicializar el driver.")
            return

        while True:
            choice = show_algorithm_menu()
            action_name, action_fn, _ = ALGORITHMS[choice]
            if action_name == "exit":
                action_fn()
                break

            action_fn(driver)
            again = input("\n¿Quieres ejecutar otro algoritmo? [s/n]: ").strip().lower()
            if again not in {"s", "si", "y", "yes"}:
                print("Saliendo del menú.")
                break

    finally:
        driver.close()


if __name__ == "__main__":
    main()