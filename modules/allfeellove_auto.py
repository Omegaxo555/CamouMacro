"""Módulo base para construir el algoritmo Allfeellove Auto."""

from __future__ import annotations

import traceback

from core.camoufox_handler import CamoufoxHandler
from modules.browser_automation import BrowserAutomation, HtmlElement


class AllfeelloveAuto:
    """Estructura base para tu algoritmo personalizado."""

    def __init__(self, driver: CamoufoxHandler):
        self.driver = driver
        self.automation = BrowserAutomation(driver.page) if driver.page else None

    def run(self) -> None:
        try:
            self._run_algorithm()
        except Exception as exc:
            print(f"[allfeellove_auto] Error al ejecutar el algoritmo: {exc}")
            traceback.print_exc()
            raise

    def _run_algorithm(self) -> None:
        """Implementa aquí tu algoritmo personalizado."""
        print("[allfeellove_auto] El algoritmo está listo para desarrollarse.")
        print("[allfeellove_auto] Completa la lógica dentro de AllfeelloveAuto.run().")

        if not self.driver.page:
            print("[allfeellove_auto] El navegador no está inicializado.")
            return

        self.automation = BrowserAutomation(self.driver.page)
        print(f"[allfeellove_auto] Navegando a https://allfeellove.com")
        self.driver.navigate("https://allfeellove.com")
        self.driver.page.wait_for_load_state("domcontentloaded")

        # Ejemplo de uso con la clase reutilizable.
        # Estos selectores deben adaptarse al HTML real de la página.
        gender_button = HtmlElement.css("[data-testid='gender-option-male']")
        name_input = HtmlElement.css("input[name='name']")
        date_input = HtmlElement.css("input[type='date']")
        terms_checkbox = HtmlElement.css("input[type='checkbox']")

        print(f"[allfeellove_auto] Intentando click en: {gender_button}")
        self.automation.safe_click(gender_button)

        print(f"[allfeellove_auto] Intentando completar el nombre.")
        self.automation.human_type(name_input, "Thompsom")

        print(f"[allfeellove_auto] Intentando completar fecha.")
        self.automation.select_date(date_input, "1990-01-01")

        print(f"[allfeellove_auto] Intentando checkbox de términos.")
        self.automation.check_checkbox(terms_checkbox, check=True)


def run_allfeellove_auto(driver: CamoufoxHandler) -> None:
    """Wrapper para ejecutar el algoritmo personalizado."""
    algorithm = AllfeelloveAuto(driver)
    algorithm.run()
