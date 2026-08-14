#!/usr/bin/env python3
"""Genera una plantilla de perfil persistente para Camoufox y la comprime como .tar.gz."""

from __future__ import annotations

import shutil
import tarfile
from pathlib import Path
import platform

from camoufox.sync_api import Camoufox

ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT / "templates" / "perfil_base"
ARCHIVE_PATH = ROOT / "templates" / "perfil_base.tar.gz"

def ensure_clean_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for child in path.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

def build_profile_template() -> Path:
    ensure_clean_dir(TEMPLATE_DIR)

    system_name = platform.system().lower()
    if system_name.startswith("linux"):
        os_value = "linux"
    elif system_name.startswith("windows"):
        os_value = "windows"
    else:
        os_value = "mac"

    print(f"Creando plantilla de perfil en: {TEMPLATE_DIR}")
    print(f"Sistema detectado: {system_name} -> os={os_value}")

    browser = Camoufox(
        persistent_context=True,
        user_data_dir=str(TEMPLATE_DIR),
        headless=True,
        humanize=True,
        os=os_value,
        geoip=True,
        proxy={"server": "socks5://127.0.0.1:9050"},
    )

    try:
        with browser:
            page = browser.new_page()
            page.goto("https://example.com", wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
    finally:
        pass

    ARCHIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(ARCHIVE_PATH, "w:gz") as tar:
        tar.add(TEMPLATE_DIR, arcname="perfil_base")

    print(f"Plantilla generada: {ARCHIVE_PATH}")
    return ARCHIVE_PATH

if __name__ == "__main__":
    build_profile_template()