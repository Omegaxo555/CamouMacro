"""Herramientas reutilizables para automatización humana de formularios y navegación."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from playwright.async_api import Error as PlaywrightError, Locator, Page


@dataclass(frozen=True)
class HtmlElement:
    """Representa un elemento HTML con un selector reutilizable y legible."""

    selector: str
    kind: str = "css"

    @classmethod
    def css(cls, selector: str) -> "HtmlElement":
        return cls(selector=selector, kind="css")

    @classmethod
    def xpath(cls, selector: str) -> "HtmlElement":
        return cls(selector=selector, kind="xpath")

    @classmethod
    def text(cls, text: str) -> "HtmlElement":
        return cls(selector=text, kind="text")

    def to_selector(self) -> str:
        if self.kind == "xpath":
            return f"xpath={self.selector}"
        if self.kind == "text":
            return f"text={self.selector}"
        return self.selector


class BrowserAutomation:
    """Clase utilitaria con buenas prácticas para automatización web humana.

    Está pensada para importarse en cualquier algoritmo y encapsular las operaciones
    frecuentes: seleccionar elementos, escribir texto, hacer clics, scroll, fechas,
    validaciones y waits controlados.
    """

    def __init__(self, page: Page, default_timeout: int = 10000, debug: bool = True):
        self.page = page
        self.default_timeout = default_timeout
        self.debug = debug

    def _debug(self, message: str) -> None:
        if self.debug:
            print(f"[browser_automation] {message}")

    # ------------------------------------------------------------------
    # Localización y espera
    # ------------------------------------------------------------------

    def resolve_selector(self, target: Union[str, HtmlElement]) -> str:
        if isinstance(target, HtmlElement):
            return target.to_selector()
        return str(target)

    def locator(self, selector: Union[str, HtmlElement], timeout: Optional[int] = None) -> Locator:
        """Devuelve un locator robusto, soportando CSS, XPath, texto o HtmlElement."""
        resolved = self.resolve_selector(selector)
        if resolved.strip().lower().startswith("xpath="):
            return self.page.locator(resolved)
        if resolved.strip().lower().startswith("text="):
            return self.page.get_by_text(resolved.replace("text=", "", 1), exact=False)
        return self.page.locator(resolved)

    def find(self, target: Union[str, HtmlElement], timeout: Optional[int] = None) -> Locator:
        """Busca un elemento por selector o por HtmlElement."""
        resolved = self.resolve_selector(target)
        self._debug(f"Buscando elemento: {resolved}")
        locator = self.locator(target, timeout)
        try:
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            self._debug(f"Elemento encontrado: {resolved}")
            return locator
        except PlaywrightError:
            self._debug(f"Elemento NO encontrado: {resolved}")
            raise


    def wait_for_visible(self, selector: Union[str, HtmlElement], timeout: Optional[int] = None) -> bool:
        try:
            self.locator(selector, timeout).wait_for(state="visible", timeout=timeout or self.default_timeout)
            return True
        except PlaywrightError:
            return False

    def wait_for_any(self, selectors: Iterable[str], timeout: Optional[int] = None) -> Optional[str]:
        timeout = timeout or self.default_timeout
        for selector in selectors:
            try:
                self.page.wait_for_selector(selector, state="visible", timeout=timeout)
                return selector
            except PlaywrightError:
                continue
        return None

    # ------------------------------------------------------------------
    # Escritura humana
    # ------------------------------------------------------------------

    def human_type(
        self,
        selector: Union[str, HtmlElement],
        text: str,
        clear_first: bool = True,
        min_delay: int = 30,
        max_delay: int = 90,
        timeout: Optional[int] = None,
    ) -> bool:
        resolved = self.resolve_selector(selector)
        self._debug(f"Intentando escribir en '{resolved}' -> '{text}'")
        try:
            locator = self.locator(selector, timeout)
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            locator.scroll_into_view_if_needed()
            locator.click()

            if clear_first:
                self.page.keyboard.press("Control+A")
                self.page.keyboard.press("Backspace")
                time.sleep(random.uniform(0.1, 0.25))

            for char in text:
                self.page.keyboard.type(char, delay=random.randint(min_delay, max_delay))
                time.sleep(random.uniform(0.01, 0.05))

            self._debug(f"Escritura completada en '{resolved}'")
            return True
        except PlaywrightError as exc:
            self._debug(f"Fallo al escribir en '{resolved}': {exc}")
            return False

    def fill(self, target: Union[str, HtmlElement], value: str, **kwargs) -> bool:
        """Rellena un campo usando selector CSS/XPath o un HtmlElement."""
        return self.human_type(target, value, **kwargs)

    def fill_fields(self, values: Dict[Union[str, HtmlElement], str], delay_range: Tuple[int, int] = (30, 90)) -> bool:
        for selector, value in values.items():
            if not self.human_type(selector, str(value), min_delay=delay_range[0], max_delay=delay_range[1]):
                return False
            time.sleep(random.uniform(0.1, 0.3))
        return True

    # ------------------------------------------------------------------
    # Clicks seguros
    # ------------------------------------------------------------------

    def safe_click(
        self,
        selector: Union[str, HtmlElement],
        timeout: Optional[int] = None,
        force: bool = False,
        click_count: int = 1,
    ) -> bool:
        resolved = self.resolve_selector(selector)
        self._debug(f"Intentando click en '{resolved}'")
        timeout_value = timeout or self.default_timeout

        try:
            locator = self.locator(selector, timeout_value)
            locator.wait_for(state="visible", timeout=timeout_value)

            # Playwright ya hace el scroll necesario antes del click.
            # No hacer scroll manual ni hover aquí porque eso dispara más
            # movimientos del viewport y puede repetir la acción varias veces.
            try:
                locator.click(force=force, click_count=click_count)
                self._debug(f"Click exitoso en '{resolved}'")
                return True
            except PlaywrightError:
                # Fallback conservador: un click por JS si el navegador bloquea
                # el click standard por overlay o intercepciones visuales.
                element = locator.element_handle()
                if element is None:
                    raise
                self.page.evaluate("(el) => el.click()", element)
                self._debug(f"Click por fallback JS exitoso en '{resolved}'")
                return True
        except PlaywrightError as exc:
            self._debug(f"Fallo al hacer click en '{resolved}': {exc}")
            return False

    def click(self, target: Union[str, HtmlElement], **kwargs) -> bool:
        """Hace click directo sobre un selector o elemento HTML."""
        return self.safe_click(target, **kwargs)

    def safe_click_text(self, text: str, exact: bool = True, timeout: Optional[int] = None) -> bool:
        try:
            self.page.get_by_text(text, exact=exact).first.wait_for(state="visible", timeout=timeout or self.default_timeout)
            self.page.get_by_text(text, exact=exact).first.click()
            return True
        except PlaywrightError:
            return False

    # ------------------------------------------------------------------
    # Radios, checks, selects y fechas
    # ------------------------------------------------------------------

    def select_option(self, selector: Union[str, HtmlElement], value: str, timeout: Optional[int] = None) -> bool:
        try:
            locator = self.locator(selector, timeout)
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            locator.select_option(value=value)
            return True
        except PlaywrightError:
            return False

    def choose_radio_by_label(self, label_text: str, timeout: Optional[int] = None) -> bool:
        try:
            self.page.locator(f"label:has-text('{label_text}')").first.wait_for(state="visible", timeout=timeout or self.default_timeout)
            self.page.locator(f"label:has-text('{label_text}')").first.click()
            return True
        except PlaywrightError:
            return False

    def check_checkbox(self, selector: str, check: bool = True, timeout: Optional[int] = None) -> bool:
        try:
            locator = self.locator(selector, timeout)
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            state = locator.is_checked()
            if check and not state:
                locator.check()
            elif not check and state:
                locator.uncheck()
            return True
        except PlaywrightError:
            return False

    def select_date(self, selector: str, date_value: str, timeout: Optional[int] = None) -> bool:
        """Ejemplo: '2026-08-14'."""
        try:
            locator = self.locator(selector, timeout)
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            locator.fill(date_value)
            return True
        except PlaywrightError:
            return False

    # ------------------------------------------------------------------
    # Scroll, foco y espera humana
    # ------------------------------------------------------------------

    def move_to_element(self, selector: str, timeout: Optional[int] = None) -> bool:
        try:
            locator = self.locator(selector, timeout)
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            locator.scroll_into_view_if_needed()
            locator.hover()
            time.sleep(random.uniform(0.2, 0.5))
            return True
        except PlaywrightError:
            return False

    def scroll_to_bottom(self, pixels: int = 800) -> None:
        self.page.evaluate(f"window.scrollBy(0, {pixels})")
        time.sleep(random.uniform(0.2, 0.5))

    def scroll_to_top(self) -> None:
        self.page.evaluate("window.scrollTo(0, 0)")
        time.sleep(random.uniform(0.2, 0.4))

    def scroll_to_selector(self, selector: str, timeout: Optional[int] = None) -> bool:
        try:
            locator = self.locator(selector, timeout)
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            locator.scroll_into_view_if_needed()
            return True
        except PlaywrightError:
            return False

    def scroll_into_view(self, selector: str, timeout: Optional[int] = None) -> bool:
        return self.scroll_to_selector(selector, timeout)

    # ------------------------------------------------------------------
    # Validación y estados
    # ------------------------------------------------------------------

    def element_exists(self, selector: Union[str, HtmlElement], timeout: Optional[int] = None) -> bool:
        resolved = self.resolve_selector(selector)
        self._debug(f"Verificando existencia de '{resolved}'")
        try:
            self.page.wait_for_selector(resolved, state="visible", timeout=timeout or self.default_timeout)
            self._debug(f"Elemento visible encontrado: '{resolved}'")
            return True
        except PlaywrightError:
            self._debug(f"Elemento no visible o no encontrado: '{resolved}'")
            return False

    def is_visible(self, selector: Union[str, HtmlElement], timeout: Optional[int] = None) -> bool:
        return self.element_exists(selector, timeout)

    def get_text(self, selector: Union[str, HtmlElement], timeout: Optional[int] = None) -> Optional[str]:
        try:
            locator = self.locator(selector, timeout)
            locator.wait_for(state="visible", timeout=timeout or self.default_timeout)
            return locator.text_content()
        except PlaywrightError:
            return None

    # ------------------------------------------------------------------
    # Submit y navegación humana
    # ------------------------------------------------------------------

    def submit_form(self, submit_selector: str, timeout: Optional[int] = None) -> bool:
        if not self.safe_click(submit_selector, timeout=timeout):
            return False
        self.page.wait_for_load_state("networkidle", timeout=timeout or self.default_timeout)
        return True

    def navigate(self, url: str, wait_until: str = "domcontentloaded") -> bool:
        try:
            self.page.goto(url, wait_until=wait_until)
            return True
        except PlaywrightError:
            return False

    def wait_human(self, min_seconds: float = 0.3, max_seconds: float = 1.2) -> None:
        time.sleep(random.uniform(min_seconds, max_seconds))


__all__ = ["BrowserAutomation", "HtmlElement"]
