#!/usr/bin/env python3
"""Instala las dependencias del proyecto en el entorno virtual activo o en .venv."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PACKAGES = [
    "camoufox",
    "playwright",
]


def get_python_executable() -> str:
    """Devuelve el intérprete del venv activo o del .venv del proyecto."""
    if os.environ.get("VIRTUAL_ENV"):
        if os.name == "nt":
            return str(Path(os.environ["VIRTUAL_ENV"]) / "Scripts" / "python.exe")
        return str(Path(os.environ["VIRTUAL_ENV"]) / "bin" / "python")

    project_root = Path(__file__).resolve().parent
    venv_python = project_root / ".venv"
    if os.name == "nt":
        venv_python = venv_python / "Scripts" / "python.exe"
    else:
        venv_python = venv_python / "bin" / "python"

    if venv_python.exists():
        print(f"Se detectó un entorno virtual en: {venv_python.parent.parent}")
        return str(venv_python)

    print("No se encontró un entorno virtual activo ni un .venv en la raíz del proyecto.")
    print("Activa el venv antes de ejecutar este archivo o crea uno con:")
    print("  python -m venv .venv")
    raise SystemExit(1)


def run_command(command: list[str]) -> None:
    print(f"\n>>> {' '.join(command)}")
    subprocess.check_call(command)


def main() -> None:
    python_exe = get_python_executable()
    print(f"Usando intérprete: {python_exe}")

    run_command([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
    run_command([python_exe, "-m", "pip", "install", *PACKAGES])

    # Playwright requiere instalar el runtime de Chromium/Firefox/WebKit.
    run_command([python_exe, "-m", "playwright", "install", "chromium"])

    print("\n✅ Dependencias instaladas correctamente.")
    print("Puedes ejecutar el proyecto con:")
    print(f"  {python_exe} main.py")


if __name__ == "__main__":
    main()
