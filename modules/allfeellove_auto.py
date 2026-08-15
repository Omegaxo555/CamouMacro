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
        self.driver.page.wait_for_timeout(1000)

        result = self.automation.safe_click(filtersButton)
        print(f'[allfeellove_auto] Abriendo el apartado de filtros: {result}')
        self.driver.page.wait_for_timeout(100)

        result = self.automation.select_multiselect_option(
            countrySelect,
            "United States",
            search_selector=countrySearchInput,
            timeout=2000,
        )
        print(f'[allfeellove_auto] País seleccionado: {result}')

        age_filter = random.choice(["41", "34", "46"])

        result = self.automation.select_multiselect_option(
            ageFromSelect,
            age_filter,
            search_selector=ageFromInput,
            timeout=5000,
        )
        print(f'[allfeellove_auto] Edad desde seleccionada: {result}')

        result = self.automation.select_multiselect_option(
            ageToSelect,
            age_filter,
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
        selectors = [
            'p[data-test-id*="person-name"]',
            'p.ui-typography.color.name',
            'p.name',
            '[data-test-id*="person person-name"]',
            '[data-test-id*="person-name" i]',
        ]

        names: list[str] = []
        for selector in selectors:
            try:
                visible_names = self.driver.page.locator(selector).all_text_contents()
                for name in visible_names:
                    cleaned = (name or "").strip()
                    if not cleaned:
                        continue
                    lowered = cleaned.lower()
                    if any(token in lowered for token in ["ad", "sponsored", "anuncio", "promo"]):
                        continue
                    names.append(cleaned)
            except Exception:
                continue

        seen = set()
        unique_names = []
        for name in names:
            if name.lower() not in seen:
                seen.add(name.lower())
                unique_names.append(name)

        return unique_names[:12]

    def _wait_for_profile_names(self, timeout_seconds: float = 8.0) -> list[str]:
        deadline = time.monotonic() + timeout_seconds
        last_names: list[str] = []
        while time.monotonic() < deadline:
            names = self._get_visible_profile_names()
            if names:
                last_names = names
                break
            self.driver.page.wait_for_timeout(400)
        return last_names

    def _normalise_text(self, value: str) -> str:
        if not value:
            return ""
        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9]+", " ", value)
        return " ".join(value.split())

    def _extract_name_and_age_from_card(self, card_locator) -> tuple[str, int | None]:
        try:
            name_text = card_locator.locator('p[data-test-id*="person-name"], p.ui-typography.color.name, p.name').first.text_content() or ""
        except Exception:
            name_text = ""

        try:
            age_text = card_locator.locator('p[data-test-id*="person-display-age"], [data-test-id*="person-display-age"], p[data-test-id*="person age"]').first.text_content() or ""
        except Exception:
            age_text = ""

        cleaned_name = self._normalise_text(name_text)
        age_match = re.search(r"(\d{1,3})", age_text or "")
        age_value = int(age_match.group(1)) if age_match else None
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

        normalised_name = self._normalise_text(target_name)
        if name_text != normalised_name:
            return False

        if age_value is None:
            return False

        return age_value == target_age

    def _find_profile_card_by_name(self, target_name: str, target_age: int = None):
        selectors = [
            'p[data-test-id*="person-name"]',
            'p.ui-typography.color.name',
            'p.name',
            '[data-test-id*="person person-name"]',
        ]

        for selector in selectors:
            candidates = self.driver.page.locator(selector)
            try:
                count = candidates.count()
            except Exception:
                continue

            for index in range(count):
                try:
                    candidate = candidates.nth(index)
                    if not candidate.is_visible():
                        continue
                except Exception:
                    continue

                card = None
                try:
                    search_items = self.driver.page.locator('[data-test-id*="search-item"],[data-test-id*="file:search-item"]')
                    matches = search_items.filter(has=candidate)
                    if matches.count() > 0:
                        card = matches.first
                    else:
                        card = candidate.locator("xpath=ancestor::*[contains(@data-test-id,'search-item')][1]")
                        if card.count() == 0:
                            card = candidate.locator("xpath=ancestor::*[contains(@class,'info-wrapper')][1]")
                        if card.count() == 0:
                            card = candidate.locator("xpath=ancestor::*[contains(@class,'info')][1]")
                        if card.count() == 0:
                            card = candidate.locator("xpath=ancestor::*[self::div or self::article or self::section][1]")
                except Exception:
                    card = None

                if card is None or card.count() == 0:
                    continue

                if target_age is not None:
                    if self._card_matches_target_profile(card, target_name, target_age):
                        return card
                else:
                    name_text, _ = self._extract_name_and_age_from_card(card)
                    if self._normalise_text(target_name) == name_text:
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

    def _interact_with_found_profile(self, card_locator) -> None:
        view_profile_selector = 'button[data-test-id="cmp:ui-button click:go-to-profile-via-button"]'
        like_selector = 'button[data-test-id="cmp:ui-button click:on-like"]'
        wink_selector = 'button[data-test-id="cmp:ui-button click:on-wink"]'
        textarea_selector = 'textarea[data-test-id="cmp:ui-textarea message type-your-message"]'
        send_selector = 'button[data-test-id="cmp:ui-button click:send-message send"]'

        try:
            view_button = card_locator.locator(view_profile_selector)
            if view_button.count() == 0:
                view_button = self.driver.page.locator(view_profile_selector).first
            view_button.wait_for(state="visible", timeout=15000)
            view_button.click()
            print(f"[allfeellove_auto] Se abrió el perfil de '{self.last_found_profile_name}'.")
        except Exception as exc:
            print(f"[allfeellove_auto] No se pudo abrir el perfil: {exc}")
            return
        
        try:
            like_button = self.driver.page.locator(like_selector)
            if like_button.count() > 0:
                like_button.first.wait_for(state="visible", timeout=15000)
                like_button.first.click()
                print(f"[allfeellove_auto] Like enviado a '{self.last_found_profile_name}'.")
        except Exception as exc:
            print(f"[allfeellove_auto] No se pudo dar Like: {exc}")

        try:
            wink_button = self.driver.page.locator(wink_selector)
            if wink_button.count() > 0:
                wink_button.first.wait_for(state="visible", timeout=15000)
                wink_button.first.click()
                print(f"[allfeellove_auto] Wink enviado a '{self.last_found_profile_name}'.")
        except Exception as exc:
            print(f"[allfeellove_auto] No se pudo enviar wink: {exc}")

        try:
            self.driver.page.wait_for_selector(textarea_selector, state="visible", timeout=20000)
        except Exception:
            print(f"[allfeellove_auto] La vista del perfil no está lista; no se pudo abrir el textarea del mensaje.")
            return

        tone = random.choice(["flirty", "casual", "premium"])
        messages = PeopleTalkGenerator.build_message_set(
            count=5,
            name=self.last_found_profile_name,
            age=self.last_found_profile_age,
            personality="warm, playful, and confident",
            tone=tone,
        )

        for index, message in enumerate(messages, start=1):
            try:
                self.driver.page.wait_for_selector(textarea_selector, state="visible", timeout=20000)
                self.automation.human_type(textarea_selector, message)
                self.automation.safe_click(send_selector)
                print(f"[allfeellove_auto] Mensaje {index}/5 enviado: {message}")
            except Exception as exc:
                print(f"[allfeellove_auto] Error al enviar mensaje {index}/5: {exc}")
                break

            if index < len(messages):
                print(f"[allfeellove_auto] Esperando 5 segundos antes del siguiente mensaje...")
                self.driver.page.wait_for_timeout(5000)

    def _go_to_next_profile_page(self) -> bool:
        next_page_selector = (
            'button[data-test-id="cmp:ui-button click:change-page-options-current-page next"]'
        )

        for attempt in range(1, 6):
            try:
                next_button = self.driver.page.locator(next_page_selector)
                if next_button.count() > 0 and next_button.first.is_visible():
                    self.driver.page.wait_for_timeout(3000)
                    next_button.first.click()
                    self.driver.page.wait_for_load_state("networkidle", timeout=self.driver.timeout)
                    return True
            except Exception:
                pass

            self.driver.page.wait_for_timeout(1000)

        return False

    def _scan_profiles_until_found(self, target_profiles: dict[str, int], max_pages: int = 25) -> bool:
        for page_index in range(1, max_pages + 1):
            visible_names = self._wait_for_profile_names(timeout_seconds=8.0)
            print(f"[allfeellove_auto] Página {page_index}. Nombres visibles: {visible_names[:12]}")

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
