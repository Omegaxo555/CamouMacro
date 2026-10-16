"""Módulo base para construir tu algoritmo personalizado adaptable por género."""

from __future__ import annotations
import os
from typing import Optional

from core.camoufox_handler import CamoufoxHandler
from modules.InfoGeneration.peopleInfo_generator import PeopleInfoGenerator
from modules.InfoGeneration.peopleTalk_generator import PeopleTalkGenerator


class CustomAlgorithm:
    """Estructura base para tu algoritmo adaptable a personas masculinas o femeninas.

    Mantén la lógica organizada en métodos pequeños y reutilizables.
    """

    def __init__(
        self,
        driver: CamoufoxHandler,
        gender: Optional[str] = None,
        target_gender: Optional[str] = None,
    ):
        self.driver = driver
        # Resolver géneros desde parámetros o variables de entorno
        self.gender = gender or os.environ.get("ACCOUNT_GENDER", "male")
        self.target_gender = target_gender or os.environ.get("TARGET_GENDER", "women")

        # Generar persona adaptable
        self.profile = PeopleInfoGenerator.generate_profile(
            gender=self.gender,
            looking_for=self.target_gender,
        )

    def run(self) -> None:
        """Implementa aquí tu algoritmo personalizado."""
        print(f"[custom_algorithm] Iniciando algoritmo para {self.profile['name']} ({self.profile['gender']})")
        print(f"[custom_algorithm] Género objetivo: {self.target_gender}")

        if not self.driver.page:
            print("[custom_algorithm] El navegador no está inicializado.")
            return

        # Ejemplo de mensajes generados según el género objetivo
        messages = PeopleTalkGenerator.build_message_set(
            count=3,
            name="Alex",
            target_gender=self.target_gender,
            tone="flirty",
        )
        print(f"[custom_algorithm] Mensajes de ejemplo listos ({len(messages)} mensajes)")


def run_custom_algorithm(
    driver: CamoufoxHandler,
    gender: Optional[str] = None,
    target_gender: Optional[str] = None,
) -> None:
    """Wrapper simple para ejecutar el algoritmo personalizado."""
    algorithm = CustomAlgorithm(driver, gender=gender, target_gender=target_gender)
    algorithm.run()
