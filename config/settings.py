"""Configuración global de automatización y tiempos de ejecución."""

import json
import os
import re
from pathlib import Path


class AutomationConfig:
    """Parámetros de velocidad, delays y rutas para los algoritmos.

    Los valores se leen primero desde variables de entorno (para que la GUI
    pueda pasarlos al lanzar terminales emergentes), y si no existen, se usan
    los valores por defecto definidos aquí.
    """

    # Factor global multiplicador de tiempos y esperas.
    SPEED_FACTOR: float = float(os.environ.get("SPEED_FACTOR", "1.0"))

    # Ruta del archivo con el diccionario de perfiles objetivo
    TARGETS_FILE: str = os.environ.get("TARGETS_FILE", "targets/profiles_dict.txt")

    # Género objetivo ("women" / "men") y de la cuenta ("men" / "women" / "auto")
    TARGET_GENDER: str = os.environ.get("TARGET_GENDER", "")
    ACCOUNT_GENDER: str = os.environ.get("ACCOUNT_GENDER", "")

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
        """Localiza la ruta absoluta al archivo de targets."""
        candidate = Path(cls.TARGETS_FILE)
        if candidate.is_absolute() and candidate.is_file():
            return candidate

        root = Path(__file__).resolve().parent.parent
        options = [
            root / cls.TARGETS_FILE,
            Path.cwd() / cls.TARGETS_FILE,
            root / "targets" / "profiles_dict.txt",
            root / "python_engine" / "targets" / "profiles_dict.txt",
            Path.cwd() / "targets" / "profiles_dict.txt",
            Path.cwd() / "python_engine" / "targets" / "profiles_dict.txt",
        ]
        for opt in options:
            if opt.is_file():
                return opt
        return root / cls.TARGETS_FILE

    @classmethod
    def normalize_gender(cls, value: str | None, default: str = "women") -> str:
        """Normaliza cadenas de género a 'men' o 'women'."""
        if not value:
            return default
        val = str(value).strip().lower()
        if val in ("men", "man", "male", "m", "hombre", "hombres", "masculino", "chico"):
            return "men"
        if val in ("women", "woman", "female", "f", "mujer", "mujeres", "femenina", "femenino", "chica"):
            return "women"
        return default

    @classmethod
    def load_profiles_config(cls, custom_path: str | Path | None = None) -> tuple[str, str, dict[str, int]]:
        """Carga y parsea la configuración de profiles_dict.txt.

        Soporta:
        1. Formato estructurado moderno:
           {
             "target_gender": "women",   # o "men"
             "account_gender": "men",   # opcional (si no está, se deduce opuesto)
             "targets": {"Zol": 41, "Anna": 46}
           }
        2. Formato con lista de objetos:
           {
             "target_gender": "men",
             "targets": [{"name": "Alex", "age": 35}]
           }
        3. Formato plano retrocompatible:
           {
             "target_gender": "women",
             "Zol": 41,
             "Anna": 46
           }
        4. Formato clásico heredado:
           {
             "Zol": 41,
             "Anna": 46
           }

        Devuelve:
            (target_gender, account_gender, targets_dict)
            donde target_gender es 'men' o 'women'
            y account_gender es 'men' o 'women'.
        """
        path = Path(custom_path) if custom_path else cls.get_targets_path()
        file_target_gender = None
        file_account_gender = None
        targets: dict[str, int] = {}

        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    # Extraer claves de metadatos de género
                    for k, v in data.items():
                        k_lower = k.lower().strip()
                        if k_lower in ("target_gender", "targetgender", "target"):
                            file_target_gender = cls.normalize_gender(v)
                        elif k_lower in ("account_gender", "accountgender", "my_gender", "user_gender", "usergender"):
                            file_account_gender = cls.normalize_gender(v)
                        elif k_lower == "gender":
                            file_target_gender = cls.normalize_gender(v)

                    # Extraer objetivos
                    raw_targets = data.get("targets") or data.get("profiles")
                    if isinstance(raw_targets, dict):
                        for name, age in raw_targets.items():
                            try:
                                targets[str(name).strip()] = int(age)
                            except (ValueError, TypeError):
                                pass
                    elif isinstance(raw_targets, list):
                        for item in raw_targets:
                            if isinstance(item, dict) and "name" in item:
                                try:
                                    name_val = str(item["name"]).strip()
                                    age_val = int(item.get("age", 0))
                                    targets[name_val] = age_val
                                except (ValueError, TypeError):
                                    pass
                    else:
                        # Formato plano: llaves directas que no sean metadatos
                        meta_keys = {
                            "target_gender", "targetgender", "account_gender",
                            "accountgender", "my_gender", "user_gender", "gender", "target"
                        }
                        for k, v in data.items():
                            if k.lower().strip() not in meta_keys:
                                try:
                                    targets[str(k).strip()] = int(v)
                                except (ValueError, TypeError):
                                    pass
            except Exception as exc:
                print(f"[config] Aviso: Error al parsear {path}: {exc}")

        # Si no se encontraron targets en el archivo, fallback por defecto
        if not targets:
            targets = {"Zol": 41, "Anna": 46, "Kathe": 34}

        # Resolver target_gender: Variable de entorno > Archivo > Default ("women")
        env_target = os.environ.get("TARGET_GENDER")
        if env_target:
            target_gender = cls.normalize_gender(env_target)
        elif file_target_gender:
            target_gender = file_target_gender
        else:
            target_gender = "women"

        # Resolver account_gender: Variable de entorno > Archivo > Opuesto a target_gender
        env_account = os.environ.get("ACCOUNT_GENDER")
        if env_account and env_account.lower() != "auto":
            account_gender = cls.normalize_gender(env_account)
        elif file_account_gender and file_account_gender.lower() != "auto":
            account_gender = file_account_gender
        else:
            # Opuesto automático al target
            account_gender = "men" if target_gender == "women" else "women"

        return target_gender, account_gender, targets
