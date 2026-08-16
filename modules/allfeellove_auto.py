"""Módulo base para construir el algoritmo Allfeellove Auto."""

from __future__ import annotations
import random
import re
import time
import traceback

from core.camoufox_handler import CamoufoxHandler
from modules.browser_automation import BrowserAutomation, HtmlElement
from modules.InfoGeneration.peopleInfo_generator import PeopleInfoGenerator
from modules.InfoGeneration.peopleTalk_generator import PeopleTalkGenerator


class AllfeelloveAuto:
    """Estructura base para tu algoritmo personalizado."""

    def __init__(self, driver: CamoufoxHandler):
        self.driver = driver
        self.automation = BrowserAutomation(driver.page) if driver.page else None
        self.last_found_profile_name: str | None = None
        self.last_found_profile_age: int | None = None

    def run(self) -> None:
        try:
            self.profile_dict = PeopleInfoGenerator.generate_profile()
            print(f"[allfeellove_auto] Iniciando algoritmo para perfil de {self.profile_dict['name']}")
            self._run_algorithm()
        except Exception as exc:
            print(f"[allfeellove_auto] Error al ejecutar el algoritmo: {exc}")
            traceback.print_exc()
            raise

    def _run_algorithm(self) -> None:
        print("[allfeellove_auto] El algoritmo está listo para desarrollarse.")
        print("[allfeellove_auto] Completa la lógica dentro de AllfeelloveAuto.run().")

        if not self.driver.page:
            print("[allfeellove_auto] El navegador no está inicializado.")
            return

        self.automation = BrowserAutomation(self.driver.page, debug=True)
        print(f"[allfeellove_auto] Navegando a https://allfeellove.com")
        if not self.driver.navigate("https://allfeellove.com"):
            print("[allfeellove_auto] No se pudo cargar la página. Revisa red, DNS, firewall o el sitio.")
            return
        if self.driver.is_cloudflare_blocked():
                    print("[allfeellove_auto] Detectado bloqueo de Cloudflare. Reiniciando navegador con otra salida de red...")
                    if not self.driver.rotate_connection(use_tor=True):
                        print("[allfeellove_auto] No se pudo rotar la conexión para evitar el bloqueo.")
                        return
                    if not self.driver.navigate("https://allfeellove.com"):
                        print("[allfeellove_auto] La página sigue bloqueada después del reinicio.")
                        return

        self.driver.page.wait_for_load_state("domcontentloaded", timeout=self.driver.timeout)
        print(f"[allfeellove_auto] Página cargada. URL actual: {self.driver.page.url}")

        cookies_button = HtmlElement.xpath('/html/body/div[2]/div/div/div/div/div[2]/div[1]/button[1]')
        gender_button = HtmlElement.css("label.gender__item.male")
        lookingfor_button = HtmlElement.css('label.checkbox__item.woman.woman_female')
        name_input = HtmlElement.css('input.input.input_name.name-container__input')
        date_input = HtmlElement.xpath('/html/body/div[1]/div/div/main/div[1]/div/div[2]/div/div/form/div[3]/div[2]/div[1]/input')
        terms_checkbox = HtmlElement.xpath("/html/body/div[1]/div/div/main/div[1]/div/div[2]/div/div/form/div[4]/div[1]/div[1]/label")
        submit_button = HtmlElement.xpath('/html/body/div[1]/div/div/main/div[1]/div/div[2]/div/div/form/button')
        
        mail_input = HtmlElement.xpath('/html/body/div/div/div/main/div[1]/div/div/div/div/form/div[1]/div[1]/input')
        password_input = HtmlElement.xpath('/html/body/div/div/div/main/div[1]/div/div/div/div/form/div[2]/div[1]/div/input')
        signup_button = HtmlElement.xpath('/html/body/div/div/div/main/div[1]/div/div/div/div/form/button')

        for label, selector in {
            "genero": gender_button,
            "busqueda": lookingfor_button,
            "nombre": name_input,
            "fecha": date_input,
            "terminos": terms_checkbox,
            "enviar": submit_button
        }.items():
            print(f"[allfeellove_auto] Verificando selector de {label}: {selector}")
            exists = self.automation.element_exists(selector)
            print(f"[allfeellove_auto] ¿Existe {label}? {exists}")
            if not exists:
                print(f"[allfeellove_auto] No existe el elemento de {label}. Revisa el selector o la carga de la página.")
                return

        if self.automation.element_exists(cookies_button):
            print(f"[allfeellove_auto] Intentando click en: {cookies_button}")
            result = self.automation.safe_click(cookies_button)
            print(f"[allfeellove_auto] Resultado click cookies: {result}")
        else:
            print(f"[allfeellove_auto] Cookies_button not found")

        print(f"[allfeellove_auto] Intentando click en: {gender_button}")
        result = self.automation.safe_click(gender_button)
        print(f"[allfeellove_auto] Resultado click género: {result}")

        print(f"[allfeellove_auto] Intentando click en: {lookingfor_button}")
        result = self.automation.safe_click(lookingfor_button)
        print(f"[allfeellove_auto] Resultado click búsqueda: {result}")

        print(f"[allfeellove_auto] Intentando completar el nombre.")
        result = self.automation.human_type(name_input, self.profile_dict['name'])
        print(f"[allfeellove_auto] Resultado nombre: {result}")

        print(f"[allfeellove_auto] Intentando completar fecha. {self.profile_dict['birthdate']}")
        result = self.automation.human_type(date_input, self.profile_dict['birthdate'])
        print(f"[allfeellove_auto] Resultado fecha: {result}")

        print(f"[allfeellove_auto] Intentando checkbox de términos.")
        result = self.automation.check_checkbox(terms_checkbox, check=True)
        print(f"[allfeellove_auto] Resultado términos: {result}")

        print(f"[allfeellove_auto] Intentando click en: {submit_button}")
        result = self.automation.safe_click(submit_button)
        print(f"[allfeellove_auto] Resultado click enviar: {result}")

        self.driver.page.wait_for_load_state("domcontentloaded", timeout=self.driver.timeout)

        result = self.automation.human_type(mail_input, self.profile_dict['email'])
        print(f"[allfeellove_auto] Verificando existencia de input de mail: {result}")

        result = self.automation.human_type(password_input, "self.profile_dict['password']")
        print(f"[allfeellove_auto] Verificando existencia de input de password: {result}")

        self.automation.safe_click(HtmlElement.css('div.google-button-wrapper'))
        result = self.automation.safe_click(signup_button)
        print(f"[allfeellove_auto] Verificando existencia de botón de signup: {result}")

        #--------Saltando a la reclamar los credits-------#

        print('[allfeellove_auto] Esperando por inicio de sesion 1Minute-aprox')
        self.driver.page.wait_for_load_state("domcontentloaded", timeout=self.driver.timeout)

        nextLets_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:next Let’s do it!"]')
        nextStep_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:skip skip"]')
        nextStep2_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:pref-gender female"]')
        nextStep3_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:skip skip"]')
        nextStep4_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:onSkip Skip"]')
        nextStep5_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:next Continue"]')
        claimtokens = HtmlElement.css('[data-test-id="cmp:button-new click:claim-welcome-bonus"]')
        cancelEmailConfirm = HtmlElement.css('#Close')

        self.automation.wait_for_visible(nextLets_button, timeout=160000)
        result = self.automation.safe_click(nextLets_button)
        print(f"[allfeellove_auto] Verificando existencia de botón de skip1: {result}")

        self.automation.wait_for_visible(nextStep_button, timeout=10000)
        result = self.automation.safe_click(nextStep_button)
        print(f"[allfeellove_auto] Verificando existencia de botón de skip1: {result}")
        
        self.automation.wait_for_visible(nextStep2_button, timeout=10000)
        result = self.automation.safe_click(nextStep2_button)
        print(f"[allfeellove_auto] Verificando existencia de botón de skip1: {result}")

        self.automation.wait_for_visible(nextStep3_button, timeout=10000)
        result = self.automation.safe_click(nextStep3_button)
        print(f"[allfeellove_auto] Verificando existencia de botón de skip1: {result}")

        self.automation.wait_for_visible(nextStep4_button, timeout=10000)
        result = self.automation.safe_click(nextStep4_button)
        print(f"[allfeellove_auto] Verificando existencia de botón de skip1: {result}")

        self.automation.wait_for_visible(nextStep5_button, timeout=10000)
        result = self.automation.safe_click(nextStep5_button)
        print(f"[allfeellove_auto] Verificando existencia de botón de skip1: {result}")

        self.automation.wait_for_visible(claimtokens, timeout=10000)
        result = self.automation.safe_click(claimtokens)
        print(f'--------------------------Se han reclamado 20 tokens----------------')

        self.automation.wait_for_visible(cancelEmailConfirm, timeout=10000)
        result = self.automation.safe_click(cancelEmailConfirm)

        #------------Busqueda de los perfiles-----------#

        accountSearch = HtmlElement.css('#AccountSearch')
        allpeopleButton = HtmlElement.css('label.chip-root[data-test-id="file:extend-search click:change-online-filter-false all"]')
        filtersButton = HtmlElement.css('[data-test-id="file:extend-search click:show-filter filters"]')

        countrySelect = HtmlElement.css('div.multiselect[role="combobox"][data-test-id="cmp:ui-select search-country select-country"]')
        countrySearchInput = HtmlElement.css('div.multiselect[role="combobox"][data-test-id="cmp:ui-select search-country select-country"] input.multiselect__input')

        ageFromSelect = HtmlElement.css('div.multiselect[role="combobox"][data-test-id="cmp:ui-select search-age-from from"]')
        ageFromInput = HtmlElement.css('div.multiselect[role="combobox"][data-test-id="cmp:ui-select search-age-from from"] input.multiselect__input')

        ageToSelect = HtmlElement.css('div.multiselect[role="combobox"][data-test-id="cmp:ui-select search-age-to to"]')
        ageToInput = HtmlElement.css('div.multiselect[role="combobox"][data-test-id="cmp:ui-select search-age-to to"] input.multiselect__input')

        genderSelect = HtmlElement.css('div.multiselect[role="combobox"][data-test-id="cmp:ui-select search-gender"]')
        searchPeople = HtmlElement.css('button[data-test-id="cmp:ui-button click:show-people show-people"]')

        result = self.automation.safe_click(accountSearch)
        print(f"[allfeellove_auto] Iniciando la busqueda del perfil, abriendo la seccion de busqueda: {result}")
        self.driver.page.wait_for_load_state("domcontentloaded", timeout=self.driver.timeout)

        result = self.automation.safe_click(allpeopleButton)
        print(f'[allfeellove_auto] Filtrando todos: {result}')
        self.driver.page.wait_for_timeout(80)

        result = self.automation.safe_click(filtersButton)
        print(f'[allfeellove_auto] Abriendo el apartado de filtros: {result}')
        self.automation.wait_for_visible(HtmlElement.css('.search-filters-form, [data-test-id="cmp:search-filter content"]'), timeout=4000)

        result = self.automation.select_multiselect_option(
            countrySelect,
            "United States",
            search_selector=countrySearchInput,
            timeout=2000,
        )
        print(f'[allfeellove_auto] País seleccionado: {result}')

        age_filter = 41#random.choice(["41", "34", "46"])

        result = self.automation.select_multiselect_option(
            ageFromSelect,
            '41',
            search_selector=ageFromInput,
            timeout=5000,
        )
        print(f'[allfeellove_auto] Edad desde seleccionada: {result}')

        result = self.automation.select_multiselect_option(
            ageToSelect,
            '41',
            search_selector=ageToInput,
            timeout=5000,
        )
        print(f'[allfeellove_auto] Edad hasta seleccionada: {result}')

        #result = self.automation.safe_click(genderSelect)
        #print(f'[allfeellove_auto] Apertura selector de género: {result}')

        self.automation.safe_click(searchPeople)
        print(f'[allfeellove_auto] Filtros Terminados...')

        #--------------------Seccion de Buscar Perfil--------------------#
        target_profiles = {"Zol": 41, "Anna": 46, "Kathe": 34}
        found_profile = self._scan_profiles_until_found(target_profiles, max_pages=25)

        if found_profile:
            print(f"[allfeellove_auto] Búsqueda finalizada: '{self.last_found_profile_name}' ({self.last_found_profile_age}) localizado.")
        else:
            print(f"[allfeellove_auto] No se encontró ninguna de estas opciones: {target_profiles} después de revisar las páginas disponibles.")

        #---------------------Darle Like al perfil y entrar al perfil--------------------#



    def _get_visible_profile_names(self) -> list[str]:
        names: list[str] = []
        seen: set[str] = set()

        for card in self._collect_profile_cards():
            try:
                name_text, _ = self._extract_name_and_age_from_card(card)
            except Exception:
                continue

            if not name_text or name_text in seen:
                continue

            seen.add(name_text)
            names.append(name_text)

        return names[:12]

    def _wait_for_profile_names(self, timeout_seconds: float = 2.5) -> list[str]:
        deadline = time.monotonic() + timeout_seconds
        last_names: list[str] = []
        while time.monotonic() < deadline:
            names = self._get_visible_profile_names()
            if names:
                last_names = names
                break
            self.driver.page.wait_for_timeout(80)
        return last_names

    def _normalise_text(self, value: str) -> str:
        if not value:
            return ""
        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9]+", " ", value)
        return " ".join(value.split())

    def _collect_profile_cards(self):
        """Busca solo tarjetas reales de resultados, no menús ni encabezados."""
        selectors = [
            '[data-test-id*="file:search-item"]',
            'div.search-profile-card',
            '[data-test-id*="search-item"]',
        ]

        cards = []
        seen: set[str] = set()

        for selector in selectors:
            try:
                locator = self.driver.page.locator(selector)
                for index in range(min(locator.count(), 80)):
                    card = locator.nth(index)
                    try:
                        if not card.is_visible():
                            continue
                    except Exception:
                        continue

                    data_test_id = (card.get_attribute("data-test-id") or "").lower()
                    class_names = (card.get_attribute("class") or "").lower()
                    if "search-item" not in data_test_id and "search-profile-card" not in class_names:
                        continue

                    name_candidates = card.locator('p[data-test-id*="person-name"], p.ui-typography.color.name, p.name, .name').count()
                    if name_candidates == 0:
                        continue

                    identity = card.get_attribute("id") or data_test_id or str(index)
                    if identity in seen:
                        continue
                    seen.add(identity)
                    cards.append(card)
            except Exception:
                continue

        return cards

    def _extract_name_and_age_from_card(self, card_locator) -> tuple[str, int | None]:
        name_text = ""
        for selector in [
            'p[data-test-id*="person-name"]',
            'p.ui-typography.color.name',
            'p.name',
            '.name',
        ]:
            try:
                candidate = card_locator.locator(selector).first
                if candidate.count() > 0:
                    text = (candidate.text_content() or "").strip()
                    if text:
                        name_text = text
                        break
            except Exception:
                continue

        age_text = ""
        for selector in [
            'p[data-test-id*="person-display-age"]',
            '[data-test-id*="person-display-age"]',
            'p[data-test-id*="person age"]',
            '.info-wrapper p',
            '.info p',
        ]:
            try:
                candidate = card_locator.locator(selector).first
                if candidate.count() > 0:
                    text = (candidate.text_content() or "").strip()
                    if text:
                        age_text = text
                        break
            except Exception:
                continue

        cleaned_name = self._normalise_text(name_text)
        age_digits = re.findall(r"\d{1,3}", age_text or "")
        age_value = int(age_digits[-1]) if age_digits else None
        return cleaned_name, age_value

    def _card_matches_target_profile(self, card_locator, target_name: str, target_age: int) -> bool:
        if card_locator is None:
            return False

        try:
            name_text, age_value = self._extract_name_and_age_from_card(card_locator)
        except Exception:
            return False

        if not name_text:
            return False

        if name_text != self._normalise_text(target_name):
            return False

        if age_value is None:
            return False

        return age_value == target_age

    def _find_profile_card_by_name(self, target_name: str, target_age: int = None):
        target_key = self._normalise_text(target_name)
        for card in self._collect_profile_cards():
            try:
                name_text, age_value = self._extract_name_and_age_from_card(card)
            except Exception:
                continue

            if not name_text or name_text != target_key:
                continue

            if target_age is not None and age_value is not None and age_value == target_age:
                return card
            if target_age is None:
                return card
        return None

    def _has_profile_name(self, target_name: str, target_age: int = None) -> bool:
        names = self._get_visible_profile_names()
        if target_age is None:
            return any(self._normalise_text(target_name) in self._normalise_text(name).split() for name in names)

        for name in names:
            if self._card_matches_target_profile(name, target_name, target_age):
                return True
        return False

    def _find_any_matching_profile_card(self, target_profiles: dict[str, int]):
        for name_option, age_option in target_profiles.items():
            card = self._find_profile_card_by_name(name_option, age_option)
            if card is not None:
                return name_option, age_option, card
        return None, None, None

    def _scan_profile_batch_fast(self, target_profiles: dict[str, int]) -> tuple[str | None, int | None, object | None]:
        if not target_profiles:
            return None, None, None

        target_map: dict[str, tuple[str, int]] = {}
        for name, age in target_profiles.items():
            target_map[self._normalise_text(name)] = (name, age)

        for card in self._collect_profile_cards():
            try:
                name_text, age_value = self._extract_name_and_age_from_card(card)
            except Exception:
                continue

            if not name_text:
                continue

            target = target_map.get(name_text)
            if target is None:
                continue

            desired_name, desired_age = target
            if age_value is None:
                continue
            if age_value == desired_age:
                return desired_name, desired_age, card

        return None, None, None

    def _ensure_chat_mode(self) -> bool:
        """Espera a que el perfil se renderice y luego alterna Mail -> Chat si corresponde."""
        try:
            selectors = [
                'textarea[data-test-id="cmp:ui-textarea message type-your-message"]',
                'textarea[placeholder*="Type your message"]',
                'textarea#form-textarea',
            ]

            for selector in selectors:
                textarea = self.driver.page.locator(selector).first
                try:
                    if textarea.count() > 0 and textarea.is_visible():
                        print("[allfeellove_auto] Ya está en modo Chat.")
                        return True
                except Exception:
                    pass

            switch_selectors = [
                'button[data-test-id="cmp:ui-button click:is-chat-visible-true change-to-chat"]',
                'button[data-test-id*="change-to-chat"]',
                'button:has-text("Change to chat")',
                'button:has-text("SwitchMode")',
                'button:has-text("Chat")',
                'button[data-test-id*="chat"]',
            ]

            for attempt in range(10):
                for selector in selectors:
                    try:
                        textarea = self.driver.page.locator(selector).first
                        if textarea.count() > 0 and textarea.is_visible():
                            print("[allfeellove_auto] El textarea de chat está visible.")
                            return True
                    except Exception:
                        pass

                clicked_any = False
                for selector in switch_selectors:
                    try:
                        button = self.driver.page.locator(selector).first
                        if button.count() > 0 and button.is_visible():
                            print("[allfeellove_auto] Detectado modo Mail. Cambiando a Chat...")
                            button.click(force=True)
                            clicked_any = True
                            break
                    except Exception:
                        pass
                if clicked_any:
                    self.driver.page.wait_for_timeout(700)
                    continue

                mail_label = self.driver.page.get_by_text("Mail", exact=False)
                if mail_label.count() > 0 and mail_label.first.is_visible():
                    print("[allfeellove_auto] Vista en Mail detectada por el label del sitio.")
                    for selector in switch_selectors:
                        try:
                            button = self.driver.page.locator(selector).first
                            if button.count() > 0:
                                button.click(force=True)
                                self.driver.page.wait_for_timeout(700)
                                break
                        except Exception:
                            pass

                self.driver.page.wait_for_timeout(250)

            return False
        except Exception as exc:
            print(f"[allfeellove_auto] No se pudo verificar el modo de chat: {exc}")
            return False

    def _send_sticker_batch(self, sticker_count: int = 3) -> None:
        toggle_selectors = [
            'button[data-test-id="click:toggle-sticker-box"]',
            'button[data-test-id*="toggle-sticker"]',
            'button:has-text("Stickers")',
        ]
        sticker_selector = 'div[data-test-id*="click:on-send-sticker-sticker"]'

        opened = False
        for selector in toggle_selectors:
            try:
                toggle_button = self.driver.page.locator(selector).first
                if toggle_button.count() > 0:
                    toggle_button.wait_for(state="visible", timeout=8000)
                    toggle_button.scroll_into_view_if_needed()
                    toggle_button.click(force=True)
                    opened = True
                    self.driver.page.wait_for_timeout(500)
                    break
            except Exception:
                pass

        if not opened:
            print("[allfeellove_auto] No se encontró el botón de stickers.")
            return

        try:
            sticker_items = self.driver.page.locator(sticker_selector)
            self.driver.page.wait_for_timeout(400)
            total_items = sticker_items.count()
            if total_items == 0:
                print("[allfeellove_auto] No hay stickers visibles en la caja.")
                return

            target_count = min(max(1, sticker_count), total_items)
            for index in range(target_count):
                item = sticker_items.nth(index)
                try:
                    item.wait_for(state="visible", timeout=5000)
                    item.scroll_into_view_if_needed()
                    item.click(force=True)
                    self.driver.page.wait_for_timeout(300)
                except Exception:
                    continue
            print(f"[allfeellove_auto] Se enviaron {target_count} stickers.")
        except Exception as exc:
            print(f"[allfeellove_auto] Error al enviar stickers: {exc}")

    def _interact_with_found_profile(self, card_locator) -> None:
        view_profile_selector = 'button[data-test-id="cmp:ui-button click:go-to-profile-via-button"]'
        like_selectors = [
            'button[data-test-id="cmp:ui-button click:on-like"]',
            'button[data-test-id*="on-like"]',
            'button:has-text("Like")',
            'button >> text=Like',
        ]
        wink_selectors = [
            'button[data-test-id="cmp:ui-button click:on-wink"]',
            'button[data-test-id*="on-wink"]',
            'button:has-text("Wink")',
            'button >> text=Wink',
        ]
        textarea_selector = 'textarea[data-test-id="cmp:ui-textarea message type-your-message"]'
        send_selector = 'button[data-test-id="cmp:ui-button click:send-message send"]'

        try:
            view_button = card_locator.locator(view_profile_selector)
            if view_button.count() == 0:
                view_button = self.driver.page.locator(view_profile_selector).first
            view_button.wait_for(state="visible", timeout=8000)
            view_button.click()
            self.driver.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.driver.page.wait_for_timeout(400)
            print(f"[allfeellove_auto] Se abrió el perfil de '{self.last_found_profile_name}'.")
        except Exception as exc:
            print(f"[allfeellove_auto] No se pudo abrir el perfil: {exc}")
            return

        self.driver.page.wait_for_timeout(1000)
        for _ in range(10):
            triggered_like = False
            triggered_wink = False

            for selector in like_selectors:
                try:
                    like_button = self.driver.page.locator(selector)
                    if like_button.count() <= 0:
                        continue

                    for index in range(like_button.count()):
                        candidate = like_button.nth(index)
                        try:
                            candidate.wait_for(state="visible", timeout=3000)
                            if candidate.is_visible():
                                candidate.click(force=True)
                                print(f"[allfeellove_auto] Like enviado a '{self.last_found_profile_name}'.")
                                triggered_like = True
                                break
                        except Exception:
                            continue
                    if triggered_like:
                        break
                except Exception:
                    pass

            if triggered_like:
                break

            for selector in wink_selectors:
                try:
                    wink_button = self.driver.page.locator(selector)
                    if wink_button.count() <= 0:
                        continue

                    for index in range(wink_button.count()):
                        candidate = wink_button.nth(index)
                        try:
                            candidate.wait_for(state="visible", timeout=3000)
                            if candidate.is_visible():
                                candidate.click(force=True)
                                print(f"[allfeellove_auto] Wink enviado a '{self.last_found_profile_name}'.")
                                triggered_wink = True
                                break
                        except Exception:
                            continue
                    if triggered_wink:
                        break
                except Exception:
                    pass

            if triggered_like or triggered_wink:
                break

            self.driver.page.wait_for_timeout(200)

        if not self._ensure_chat_mode():
            print("[allfeellove_auto] El modo Chat no se pudo activar; se cancela el flujo de mensajes.")
            return

        try:
            self.driver.page.wait_for_selector(textarea_selector, state="visible", timeout=10000)
        except Exception:
            print(f"[allfeellove_auto] La vista del perfil no está lista; no se pudo abrir el textarea del mensaje.")
            return

        tone = random.choice(["flirty", "casual", "premium"])
        messages = PeopleTalkGenerator.build_message_set(
            count=4,
            name=self.last_found_profile_name,
            age=self.last_found_profile_age,
            personality="warm, playful, and confident",
            tone=tone,
        )

        send_candidates = [
            send_selector,
            'button[data-test-id*="send-message"]',
            'button:has-text("Send")',
            'button >> text=Send',
        ]

        for index, message in enumerate(messages, start=1):
            sent = False
            for _ in range(6):
                try:
                    textarea = self.driver.page.locator(textarea_selector).first
                    if textarea.count() > 0:
                        textarea.wait_for(state="visible", timeout=5000)
                        textarea.click(force=True)
                        self.driver.page.keyboard.press("Control+A")
                        self.driver.page.keyboard.press("Backspace")
                        self.driver.page.keyboard.type(message)
                        self.driver.page.wait_for_timeout(250)

                        for candidate in send_candidates:
                            send_button = self.driver.page.locator(candidate).first
                            if send_button.count() > 0 and send_button.is_visible():
                                send_button.click(force=True)
                                sent = True
                                break

                        if sent:
                            print(f"[allfeellove_auto] Mensaje {index}/4 enviado: {message}")
                            break
                except Exception as exc:
                    print(f"[allfeellove_auto] Reintento de mensaje {index}/4: {exc}")
                    self.driver.page.wait_for_timeout(300)

            if not sent:
                print(f"[allfeellove_auto] Error al enviar mensaje {index}/4: no se pudo enviar.")
                break

            if index < len(messages):
                self.driver.page.wait_for_timeout(900)

        try:
            self._send_sticker_batch(sticker_count=3)
        except Exception as exc:
            print(f"[allfeellove_auto] No se pudieron enviar stickers: {exc}")

    def _go_to_next_profile_page(self) -> bool:
        next_page_selectors = [
            '[data-test-id="cmp:ui-button click:change-page-options-current-page next"]',
            'button[data-test-id="cmp:ui-button click:change-page-options-current-page next"]',
            'button[data-test-id*="change-page-options-current-page next"]',
            'button:has-text("Next")',
            'button >> text=Next',
            'a:has-text("Next")',
        ]

        for attempt in range(1, 6):
            for selector in next_page_selectors:
                try:
                    candidate = self.driver.page.locator(selector).first
                    if candidate.count() == 0:
                        continue
                    if candidate.is_visible():
                        self.driver.page.wait_for_timeout(800)
                        candidate.click(force=True)
                        self.driver.page.wait_for_load_state("networkidle", timeout=min(self.driver.timeout, 15000))
                        return True
                except Exception:
                    continue

            self.driver.page.wait_for_timeout(400)

        return False

    def _scan_profiles_until_found(self, target_profiles: dict[str, int], max_pages: int = 25) -> bool:
        for page_index in range(1, max_pages + 1):
            visible_names = self._wait_for_profile_names(timeout_seconds=2.5)
            print(f"[allfeellove_auto] Página {page_index}. Nombres visibles: {visible_names[:12]}")

            matched_name, matched_age, matched_card = self._scan_profile_batch_fast(target_profiles)
            if matched_card is None:
                matched_name, matched_age, matched_card = self._find_any_matching_profile_card(target_profiles)

            if matched_card is not None:
                self.last_found_profile_name = matched_name
                self.last_found_profile_age = matched_age
                print(f"[allfeellove_auto] Perfil '{matched_name}' ({matched_age}) encontrado en la página {page_index}.")
                try:
                    self._interact_with_found_profile(matched_card)
                    return True
                except Exception:
                    print(f"[allfeellove_auto] No se pudo abrir la tarjeta del perfil '{matched_name}' ({matched_age}), pero sí fue localizado.")
                    return True

            print(f"[allfeellove_auto] Ninguno de {target_profiles} fue encontrado. Avanzando con Next...")
            if not self._go_to_next_profile_page():
                print(f"[allfeellove_auto] El botón Next no está disponible. Se terminó la búsqueda.")
                return False

        return False


def run_allfeellove_auto(driver: CamoufoxHandler) -> None:
    """Wrapper para ejecutar el algoritmo personalizado."""
    algorithm = AllfeelloveAuto(driver)
    algorithm.run()
