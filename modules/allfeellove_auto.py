"""Módulo base para construir el algoritmo Allfeellove Auto."""

from __future__ import annotations

from core.camoufox_handler import CamoufoxHandler
from modules.browser_automation import BrowserAutomation as BaseBrowserAutomation

import logging


class AllfeelloveAuto:
    """Estructura base para tu algoritmo personalizado."""

    def __init__(self, driver: CamoufoxHandler):
        self.driver = driver

    def run(self) -> None:
        try:
            self._run_algorithm()
        except Exception as e:
            print(f"[allfeellove_auto] Error al ejecutar el algoritmo: {e}")

    def _run_algorithm(self) -> None:
        """Implementa aquí tu algoritmo personalizado."""
        print("[allfeellove_auto] El algoritmo está listo para desarrollarse.")
        print("[allfeellove_auto] Completa la lógica dentro de AllfeelloveAuto.run().")

        if not self.driver.page:
            print("[allfeellove_auto] El navegador no está inicializado.")
            return

        self.driver.navigate("https://allfeellove.com")

        self.driver.page.wait_for_load_state("domcontentloaded")

        ###---------Main Page---------###
        genderMale_button = HtmlElement.css("gender__item male")
        checkboxWoman_button = HtmlElement.css("[data-testid='option-woman']")
        nameContainer = HtmlElement.css("input input_name name-container__input")
        dateContainer = HtmlElement.css("[data-testid='birth-day']")
        terms_checkbox = HtmlElement.css("terms__label")

        self.automation = BaseBrowserAutomation(self.driver.page)
        self.automation.safe_click(genderMale_button)
        self.automation.safe_click(checkboxWoman_button)
        self.automation.safe_type(nameContainer, "Thompsom")
        self.automation.safe_type(dateContainer, "01/01/1990", delay=100, humanize=True)
        self.automation.safe_click(terms_checkbox, delay=100, humanize=True)



def run_allfeellove_auto(driver: CamoufoxHandler) -> None:
    """Wrapper para ejecutar el algoritmo personalizado."""
    algorithm = AllfeelloveAuto(driver)
    algorithm.run()
