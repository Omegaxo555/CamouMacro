"""Utilidades reutilizables para interacciones con el usuario en terminal."""

from __future__ import annotations

import os
import sys

try:
    import termios
    import tty
    import select
except ImportError:  # pragma: no cover
    termios = None
    tty = None
    select = None

try:
    import msvcrt
except ImportError:  # pragma: no cover
    msvcrt = None


class TerminalUI:
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

    @staticmethod
    def clear_screen() -> None:
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def press_any_key() -> None:
        if os.name == "nt":
            os.system("pause > nul")
        else:
            input("\nPresiona Enter para continuar...")

    @staticmethod
    def read_key() -> str:
        """Lee una tecla sin requerir Enter y normaliza las flechas."""
        if os.name == "nt" and msvcrt is not None:
            key = msvcrt.getwch()
            if key in {"\x00", "\xe0"}:
                extended = msvcrt.getwch()
                mapping = {
                    "H": "up",
                    "P": "down",
                    "K": "left",
                    "M": "right",
                }
                return mapping.get(extended, extended)
            if key in {"\r", "\n"}:
                return "enter"
            return key

        if termios is not None and tty is not None and sys.stdin.isatty():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                if select is not None:
                    ready, _, _ = select.select([sys.stdin], [], [], 0.2)
                    if not ready:
                        return ""
                ch = sys.stdin.read(1)
                if ch == "\x1b":
                    seq = ch + sys.stdin.read(2)
                    mapping = {
                        "\x1b[A": "up",
                        "\x1b[B": "down",
                        "\x1b[C": "right",
                        "\x1b[D": "left",
                    }
                    return mapping.get(seq, seq)
                if ch in {"\r", "\n"}:
                    return "enter"
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        ch = sys.stdin.read(1)
        if ch == "\x1b":
            seq = ch + sys.stdin.read(2)
            mapping = {
                "\x1b[A": "up",
                "\x1b[B": "down",
                "\x1b[C": "right",
                "\x1b[D": "left",
            }
            return mapping.get(seq, seq)
        if ch in {"\r", "\n"}:
            return "enter"
        return ch

    @classmethod
    def select_option(cls, title: str, options: list[str], default_index: int = 0) -> int:
        """Muestra un menú navegable por flechas y devuelve el índice seleccionado."""
        index = default_index
        while True:
            cls.clear_screen()
            print(f"{cls.ANSI['bold']}{title}{cls.ANSI['reset']}")
            print(f"{cls.ANSI['dim']}Usa ↑ ↓ o las flechas del teclado y Enter para confirmar.{cls.ANSI['reset']}\n")

            for i, option in enumerate(options):
                prefix = " > " if i == index else "   "
                color = cls.ANSI["bg_blue"] if i == index else cls.ANSI["bg_gray"]
                print(f"{color}{prefix}{option}{cls.ANSI['reset']}")

            print(f"\n{cls.ANSI['dim']}Teclas: ↑ ↓, Enter o número.{cls.ANSI['reset']}")
            key = cls.read_key().lower()

            if key in {"w", "up", "8", "a", "left"}:
                index = (index - 1) % len(options)
                continue
            if key in {"s", "down", "2", "d", "right"}:
                index = (index + 1) % len(options)
                continue
            if key in {"enter", "\r", "\n"}:
                return index
            if key.isdigit() and 1 <= int(key) <= len(options):
                return int(key) - 1

    @classmethod
    def confirm(cls, question: str, default: bool = True) -> bool:
        """Pregunta Sí/No con menú navegable."""
        options = ["Sí", "No"]
        selected = cls.select_option(f"{question}", options, default_index=0 if default else 1)
        return selected == 0

    @classmethod
    def prompt(cls, question: str, default: str = "") -> str:
        """Pide un texto al usuario y devuelve un valor seguro."""
        suffix = f" [{default}]" if default else ""
        value = input(f"{question}{suffix}: ").strip()
        return value if value else default

    @classmethod
    def info(cls, message: str) -> None:
        print(f"{cls.ANSI['fg_cyan']}{message}{cls.ANSI['reset']}")

    @classmethod
    def warning(cls, message: str) -> None:
        print(f"{cls.ANSI['fg_yellow']}{message}{cls.ANSI['reset']}")

    @classmethod
    def error(cls, message: str) -> None:
        print(f"{cls.ANSI['fg_red']}{message}{cls.ANSI['reset']}")
