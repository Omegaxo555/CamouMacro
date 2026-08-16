"""Configuración global de automatización y tiempos de ejecución."""

import os
from pathlib import Path


class AutomationConfig:
    """Parámetros de velocidad, delays y rutas para los algoritmos.

    Los valores se leen primero desde variables de entorno (para que la GUI
    pueda pasarlos al lanzar terminales emergentes), y si no existen, se usan
    los valores por defecto definidos aquí.
    """

    # Factor global multiplicador de tiempos y esperas.
    # 1.0 = Tiempo normal
    # 0.5 = Doble de rápido (mitad de tiempo en delays)
    # 0.2 = Ultra-rápido
    # 1.5 = Modo pausado / más humano
    SPEED_FACTOR: float = float(os.environ.get("SPEED_FACTOR", "1.0"))

    # Ruta del archivo con el diccionario de perfiles objetivo
    TARGETS_FILE: str = os.environ.get("TARGETS_FILE", "targets/profiles_dict.txt")

    # Límite máximo de páginas a escanear
    MAX_SCAN_PAGES: int = int(os.environ.get("MAX_SCAN_PAGES", "100"))

    # Cooldown entre envío de mensajes en segundos
    MESSAGE_COOLDOWN_SECONDS: float = float(os.environ.get("MESSAGE_COOLDOWN_SECONDS", "2.5"))

    # Cantidad de stickers a enviar
    STICKER_COUNT: int = int(os.environ.get("STICKER_COUNT", "5"))

    # Intervalo entre clics de stickers en milisegundos
    STICKER_INTERVAL_MS: int = int(os.environ.get("STICKER_INTERVAL_MS", "400"))

    # Retardo por caracter al escribir texto humano (en milisegundos)
    TYPING_MIN_DELAY_MS: int = int(os.environ.get("TYPING_MIN_DELAY_MS", "15"))
    TYPING_MAX_DELAY_MS: int = int(os.environ.get("TYPING_MAX_DELAY_MS", "45"))

    # Timeout estándar para localizar elementos (en milisegundos)
    DEFAULT_TIMEOUT_MS: int = int(os.environ.get("DEFAULT_TIMEOUT_MS", "10000"))

    @classmethod
    def delay_ms(cls, base_ms: int | float) -> int:
        """Devuelve el tiempo en milisegundos escalado por SPEED_FACTOR."""
        return max(1, int(base_ms * cls.SPEED_FACTOR))

    @classmethod
    def delay_s(cls, base_seconds: float) -> float:
        """Devuelve el tiempo en segundos escalado por SPEED_FACTOR."""
        return max(0.01, base_seconds * cls.SPEED_FACTOR)

    @classmethod
    def get_targets_path(cls) -> Path:
        return Path(__file__).resolve().parent.parent / cls.TARGETS_FILE
