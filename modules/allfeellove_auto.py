"""Módulo base para construir el algoritmo Allfeellove Auto adaptable por género."""

from __future__ import annotations
import os
import random
import re
import time
import traceback
from collections import Counter
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError

from config.settings import AutomationConfig

from core.camoufox_handler import CamoufoxHandler
from modules.browser_automation import BrowserAutomation, HtmlElement
from modules.InfoGeneration.peopleInfo_generator import PeopleInfoGenerator
from modules.InfoGeneration.peopleTalk_generator import PeopleTalkGenerator


class RegistrationError(RuntimeError):
    """Indica que una acción requerida del registro no pudo completarse."""


class AllfeelloveAuto:
    """Algoritmo Allfeellove con soporte configurable para usuarios femeninos y masculinos."""

    SITE_URL = "https://allfeellove.com"
    REGISTRATION_MAX_RETRIES = 3
    REGISTRATION_TIMEOUT_MS = 30000
    POST_SIGNUP_TIMEOUT_MS = 160000
    COOKIE_CONSENT_TIMEOUT_MS = 30000
    COOKIE_ACCEPT_BUTTON_SELECTOR = '[data-testid="cookie-popup-consent-accept-all"]'
    INCOMING_MESSAGE_SELECTOR = 'div[data-test-id="file:text-message click:resend-message"]'
    MESSAGE_REPLY_TIMEOUT_SECONDS = 5 * 60
    CREDITS_MODAL_SELECTOR = 'div[data-test-id="modal-notEnoughCredits"]'
    CREDITS_MODAL_CLOSE_SELECTOR = '[data-test-id="file:not-enough-credits-modal click:close"]'
    CREDITS_CYCLE_DELAY_MS = 30000
    STICKER_BUTTON_SELECTOR = '[data-test-id="file:add-message click:handle-stickers-by-button"]'
    STICKER_ITEM_SELECTOR = 'div[data-test-id^="file:stickers click:on-send-sticker-sticker"]'
    STICKER_SEND_PROBABILITY = 1 / 3

    def __init__(
        self,
        driver: CamoufoxHandler,
        account_gender: str | None = None,
        target_gender: str | None = None,
        targets_file: str | Path | None = None,
    ):
        self.driver = driver
        self.automation = BrowserAutomation(driver.page) if driver.page else None
        self.last_found_profile_name: str | None = None
        self.last_found_profile_age: int | None = None

        # Cargar configuración desde profiles_dict.txt y variables de entorno
        file_target, file_account, targets_dict = AutomationConfig.load_profiles_config(targets_file)

        # Resolver target_gender: Parámetro > Variable de entorno > Archivo profiles_dict.txt
        env_target = os.environ.get("TARGET_GENDER")
        if target_gender:
            self.target_gender = AutomationConfig.normalize_gender(target_gender)
        elif env_target:
            self.target_gender = AutomationConfig.normalize_gender(env_target)
        else:
            self.target_gender = file_target

        # Resolver account_gender: Parámetro > Variable de entorno > Archivo > Opuesto automático
        env_account = os.environ.get("ACCOUNT_GENDER")
        if account_gender and account_gender.lower() != "auto":
            self.account_gender = AutomationConfig.normalize_gender(account_gender)
        elif env_account and env_account.lower() != "auto":
            self.account_gender = AutomationConfig.normalize_gender(env_account)
        elif file_account and file_account.lower() != "auto":
            self.account_gender = file_account
        else:
            self.account_gender = "men" if self.target_gender == "women" else "women"

        self.target_profiles = targets_dict

        print(
            f"[allfeellove_auto] Configuración inicializada:\n"
            f"  - Cuenta a crear: {self.account_gender.upper()}\n"
            f"  - Objetivo de búsqueda: {self.target_gender.upper()}\n"
            f"  - Targets cargados ({len(self.target_profiles)}): {list(self.target_profiles.keys())}"
        )

    def _select_checkbox_option(self, testid: str) -> bool:
        if not self.driver.page or not self.automation:
            print("[allfeellove_auto] No se puede seleccionar la opción: navegador no inicializado.")
            return False

        label_locator = self.driver.page.locator(f'label[data-testid="{testid}"]')
        input_locator = label_locator.locator('input[type="checkbox"]')
        try:
            label_locator.wait_for(state="visible", timeout=10000)
            if input_locator.count() != 1:
                print(
                    f"[allfeellove_auto] Se esperaba un checkbox para '{testid}', "
                    f"encontrado: {input_locator.count()}."
                )
                return False
            if not input_locator.is_checked():
                try:
                    label_locator.click(timeout=10000)
                except PlaywrightError:
                    input_locator.check(timeout=10000)

            selected = input_locator.is_checked()
            print(f"[allfeellove_auto] Opción '{testid}' seleccionada: {selected}")
            return selected
        except PlaywrightError as exc:
            print(f"[allfeellove_auto] No se pudo seleccionar '{testid}': {exc}")
            return False

    def run(self) -> None:
        try:
            self.profile_dict = PeopleInfoGenerator.generate_profile(
                gender=self.account_gender,
                looking_for=self.target_gender,
            )
            print(
                f"[allfeellove_auto] Iniciando algoritmo para usuario '{self.profile_dict['name']}' "
                f"({self.profile_dict['gender']}) buscando ({self.profile_dict['looking_for']})"
            )
            self._run_algorithm()
        except Exception as exc:
            print(f"[allfeellove_auto] Error al ejecutar el algoritmo: {exc}")
            traceback.print_exc()
            raise

    def _click_registration_control(self, selector: HtmlElement, label: str) -> None:
        try:
            locator = self.automation.locator(selector)
            locator.wait_for(state="visible", timeout=self.REGISTRATION_TIMEOUT_MS)
            locator.click(timeout=self.REGISTRATION_TIMEOUT_MS)
        except PlaywrightError as exc:
            raise RegistrationError(f"No se pudo activar '{label}': {exc}") from exc

    def _fill_registration_field(self, selector: HtmlElement, value: str, label: str) -> None:
        if not self.automation.human_type(
            selector,
            value,
            timeout=self.REGISTRATION_TIMEOUT_MS,
        ):
            raise RegistrationError(f"No se pudo escribir el campo '{label}'.")

        try:
            actual_value = self.automation.locator(selector).input_value(
                timeout=self.REGISTRATION_TIMEOUT_MS
            )
        except PlaywrightError as exc:
            raise RegistrationError(f"No se pudo verificar el campo '{label}': {exc}") from exc

        actual = re.sub(r"\s+", " ", actual_value).strip().casefold()
        expected = re.sub(r"\s+", " ", value).strip().casefold()
        if label == "fecha de nacimiento":
            actual = re.sub(r"\D", "", actual)
            expected = re.sub(r"\D", "", expected)
        if actual != expected:
            raise RegistrationError(f"El campo '{label}' no coincide con el valor esperado.")

    def _register_account(self) -> None:
        if not self.driver.page:
            raise RegistrationError("El navegador no está inicializado.")

        self.automation = BrowserAutomation(self.driver.page, debug=True)
        print(f"[allfeellove_auto] Navegando a {self.SITE_URL}")
        if not self.driver.navigate(self.SITE_URL):
            raise RegistrationError("No se pudo cargar la página inicial.")

        if self.driver.is_cloudflare_blocked():
            print("[allfeellove_auto] Bloqueo de Cloudflare; rotando conexión antes del registro.")
            if not self.driver.rotate_connection(use_tor=True):
                raise RegistrationError("No se pudo reiniciar el navegador tras el bloqueo de Cloudflare.")
            self.automation = BrowserAutomation(self.driver.page, debug=True)
            if not self.driver.navigate(self.SITE_URL):
                raise RegistrationError("La página sigue bloqueada después de rotar la conexión.")

        try:
            self.driver.page.wait_for_load_state(
                "domcontentloaded",
                timeout=self.REGISTRATION_TIMEOUT_MS,
            )
        except PlaywrightError as exc:
            raise RegistrationError(f"La página inicial no terminó de cargar: {exc}") from exc
        print(f"[allfeellove_auto] Página cargada. URL actual: {self.driver.page.url}")

        cookies_button = HtmlElement.css(self.COOKIE_ACCEPT_BUTTON_SELECTOR)
        gender_button = (
            HtmlElement.css(
                "label.gender__item.female, label.gender__item[class*='female'], "
                "label.gender__item[class*='woman'], [data-test-id*='gender-female']"
            )
            if self.account_gender in ("women", "female")
            else HtmlElement.css(
                "label.gender__item.male, label.gender__item[class*='male'], "
                "label.gender__item[class*='man'], [data-test-id*='gender-male']"
            )
        )
        lookingfor_button = (
            HtmlElement.css('label[data-testid="option-man"]')
            if self.target_gender in ("men", "male")
            else HtmlElement.css('label[data-testid="option-woman"]')
        )
        name_input = HtmlElement.css('input.input.input_name.name-container__input')
        date_input = HtmlElement.xpath(
            '/html/body/div[1]/div/div/main/div[1]/div/div[2]/div/div/form/div[3]/div[2]/div[1]/input'
        )
        terms_checkbox = HtmlElement.xpath(
            "/html/body/div[1]/div/div/main/div[1]/div/div[2]/div/div/form/div[4]/div[1]/div[1]/label"
        )
        submit_button = HtmlElement.xpath(
            '/html/body/div[1]/div/div/main/div[1]/div/div[2]/div/div/form/button'
        )
        mail_input = HtmlElement.xpath('/html/body/div/div/div/main/div[1]/div/div/div/div/form/div[1]/div[1]/input')
        password_input = HtmlElement.xpath('/html/body/div/div/div/main/div[1]/div/div/div/div/form/div[2]/div[1]/div/input')
        signup_button = HtmlElement.xpath('/html/body/div/div/div/main/div[1]/div/div/div/div/form/button')

        if self.automation.wait_for_visible(
            cookies_button,
            timeout=self.COOKIE_CONSENT_TIMEOUT_MS,
        ):
            print("[allfeellove_auto] Esperando que el botón de cookies sea interactuable...")
            self._click_registration_control(cookies_button, "aceptar cookies")

        self._require_registration_visible(name_input, "formulario inicial")
        self._require_registration_visible(gender_button, "género de la cuenta")
        self._require_registration_visible(lookingfor_button, "preferencia de género")
        self._require_registration_visible(date_input, "fecha de nacimiento")
        self._require_registration_visible(terms_checkbox, "términos")
        self._require_registration_visible(submit_button, "botón del primer paso")

        print(f"[allfeellove_auto] Seleccionando género de cuenta ({self.account_gender}).")
        self._click_registration_control(gender_button, "género de la cuenta")

        pref_testid = "option-man" if self.target_gender in ("men", "male") else "option-woman"
        if not self._select_checkbox_option(pref_testid):
            raise RegistrationError("No se pudo seleccionar la preferencia de género.")

        print(f"[allfeellove_auto] Completando nombre: {self.profile_dict['name']}")
        self._fill_registration_field(name_input, self.profile_dict["name"], "nombre")
        print(f"[allfeellove_auto] Completando fecha de nacimiento: {self.profile_dict['birthdate']}")
        self._fill_registration_field(date_input, self.profile_dict["birthdate"], "fecha de nacimiento")

        print("[allfeellove_auto] Aceptando términos...")
        terms_selected = self.automation.check_checkbox(terms_checkbox, check=True)
        print(f"[allfeellove_auto] Resultado términos: {terms_selected}")
        if not terms_selected:
            self._click_registration_control(terms_checkbox, "aceptar términos")

        print("[allfeellove_auto] Enviando primer paso de registro...")
        self._click_registration_control(submit_button, "enviar primer paso")
        self._require_registration_visible(mail_input, "segundo paso del registro")
        self._require_registration_visible(password_input, "campo de contraseña")
        self._require_registration_visible(signup_button, "botón de registro")

        print(f"[allfeellove_auto] Completando email: {self.profile_dict['email']}")
        self._fill_registration_field(mail_input, self.profile_dict["email"], "email")
        print("[allfeellove_auto] Completando contraseña...")
        self._fill_registration_field(password_input, self.profile_dict["password"], "contraseña")

        self.automation.safe_click(HtmlElement.css('div.google-button-wrapper'))
        print("[allfeellove_auto] Enviando segundo paso de registro...")
        self._click_registration_control(signup_button, "crear cuenta")
        onboarding_button = HtmlElement.css(
            'button[data-test-id="cmp:ui-button click:next Let’s do it!"]'
        )
        if not self.automation.wait_for_visible(
            onboarding_button,
            timeout=self.POST_SIGNUP_TIMEOUT_MS,
        ):
            raise RegistrationError(
                "El segundo paso no abrió el onboarding; el registro no se confirmó."
            )

    def _require_registration_visible(self, selector: HtmlElement, label: str) -> None:
        if not self.automation.wait_for_visible(
            selector,
            timeout=self.REGISTRATION_TIMEOUT_MS,
        ):
            raise RegistrationError(f"No apareció '{label}' dentro del tiempo límite.")

    def _register_with_retries(self) -> None:
        for attempt in range(1, self.REGISTRATION_MAX_RETRIES + 2):
            try:
                print(
                    f"[allfeellove_auto] Intento de registro "
                    f"{attempt}/{self.REGISTRATION_MAX_RETRIES + 1}."
                )
                self._register_account()
                break
            except RegistrationError as exc:
                print(f"[allfeellove_auto][registro] Falló intento {attempt}: {exc}")
                if attempt > self.REGISTRATION_MAX_RETRIES:
                    raise RegistrationError(
                        f"No se pudo completar el registro tras {attempt} intentos."
                    ) from exc
                print("[allfeellove_auto][registro] Reiniciando desde la página inicial...")

    def _run_algorithm(self) -> None:
        if not self.driver.page:
            print("[allfeellove_auto] El navegador no está inicializado.")
            return

        self._register_with_retries()

        # -------- Onboarding y Reclamo de Tokens -------- #
        print('[allfeellove_auto] Esperando por inicio de sesión (onboarding)...')
        self.driver.page.wait_for_load_state("domcontentloaded", timeout=self.driver.timeout)

        # Onboarding usa botones pref-gender, distintos a los checkbox del registro.
        pref_gender = "male" if self.target_gender in ("men", "male") else "female"

        nextLets_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:next Let’s do it!"]')
        nextStep_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:skip skip"]')
        nextStep2_button = HtmlElement.css(
            f'button[data-test-id="cmp:ui-button click:pref-gender {pref_gender}"]'
        )
        nextStep3_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:skip skip"]')
        skipToStep4_button = HtmlElement.css('button[data-test-id="cmp:ui-modal click:close"]')
        nextStep4_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:skip skip"]')
        nextStep5_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:next Continue"]')
        claimtokens = HtmlElement.css('[data-test-id="cmp:button-new click:claim-welcome-bonus"]')
        cancelEmailConfirm = HtmlElement.css('button[data-test-id="cmp:ui-modal click:close"]')

        self.automation.wait_for_visible(nextLets_button, timeout=160000)
        self.automation.safe_click(nextLets_button)

        self.automation.wait_for_visible(nextStep_button, timeout=10000)
        self.automation.safe_click(nextStep_button)

        self.automation.wait_for_visible(nextStep2_button, timeout=10000)
        result = self.automation.safe_click(nextStep2_button)
        print(f"[allfeellove_auto] Resultado click preferencia onboarding: {result}")

        self.automation.wait_for_visible(nextStep3_button, timeout=10000)
        self.automation.safe_click(nextStep3_button)

        self.automation.wait_for_visible(skipToStep4_button, timeout=10000)
        self.automation.safe_click(skipToStep4_button)

        self.automation.wait_for_visible(nextStep4_button, timeout=10000)
        self.automation.safe_click(nextStep4_button)

        self.automation.wait_for_visible(nextStep5_button, timeout=10000)
        self.automation.safe_click(nextStep5_button)

        self.automation.wait_for_visible(claimtokens, timeout=10000)
        self.automation.safe_click(claimtokens)
        print('--------------------------Se han reclamado 20 tokens----------------')

        self.automation.wait_for_visible(cancelEmailConfirm, timeout=10000)
        self.automation.safe_click(cancelEmailConfirm)

        # ------------ Búsqueda y Filtros de Perfiles ----------- #
        accountSearch = HtmlElement.css(
            'a[data-test-id="file:r-u-tab-bar search"], '
            '#AccountSearch, '
            'a[href="/search"]'
        )
        allpeopleButton = HtmlElement.css('label.chip-root[data-test-id="file:extend-search click:change-online-filter-false all"]')
        filtersButton = HtmlElement.css('[data-test-id="file:extend-search click:show-filter filters"]')

        countrySelect = HtmlElement.css('div.ui-select[data-test-id="cmp:ui-select search-country select-country"]')
        countrySearchInput = HtmlElement.css('div.ui-select[data-test-id="cmp:ui-select search-country select-country"] input.multiselect__input')

        ageFromSelect = HtmlElement.css('div.ui-select[data-test-id="cmp:ui-select search-age-from from"]')
        ageFromInput = HtmlElement.css('div.ui-select[data-test-id="cmp:ui-select search-age-from from"] input.multiselect__input')

        ageToSelect = HtmlElement.css('div.ui-select[data-test-id="cmp:ui-select search-age-to to"]')
        ageToInput = HtmlElement.css('div.ui-select[data-test-id="cmp:ui-select search-age-to to"] input.multiselect__input')

        genderSelect = HtmlElement.css('div.ui-select[data-test-id="cmp:ui-select search-gender"]')
        searchPeople = HtmlElement.css('button[data-test-id="cmp:ui-button click:show-people show-people"]')

        result = self.automation.safe_click(accountSearch)
        print(f"[allfeellove_auto] Iniciando la búsqueda del perfil, abriendo la sección de búsqueda: {result}")
        self.driver.page.wait_for_load_state("domcontentloaded", timeout=self.driver.timeout)

        if AutomationConfig.SEARCH_ALL_USERS:
            result = self.automation.safe_click(allpeopleButton)
            print(f'[allfeellove_auto] Filtro ALL seleccionado: {result}')
            if not result:
                print("[allfeellove_auto] No se pudo seleccionar ALL; se cancela la búsqueda.")
                return
            self.driver.page.wait_for_timeout(80)
        else:
            print("[allfeellove_auto] Se conserva el filtro ONLY ACTIVE.")

        result = self.automation.safe_click(filtersButton)
        print(f'[allfeellove_auto] Abriendo el apartado de filtros: {result}')
        if not result or not self.automation.wait_for_visible(countrySelect, timeout=10000):
            print("[allfeellove_auto] El panel de filtros no abrió o el selector de país no apareció; se cancela la búsqueda.")
            return

        result = self.automation.select_multiselect_option(
            countrySelect,
            "United States",
            search_selector=countrySearchInput,
            timeout=5000,
        )
        print(f'[allfeellove_auto] País seleccionado: {result}')
        if not result:
            print("[allfeellove_auto] No se pudo aplicar el filtro de país; se cancela la búsqueda.")
            return

        # Selección de edad dinámica a partir de los targets cargados
        target_ages = [str(age) for age in self.target_profiles.values() if age]
        age_filter = random.choice(target_ages) if target_ages else "35"

        result = self.automation.select_multiselect_option(
            ageFromSelect,
            age_filter,
            search_selector=ageFromInput,
            timeout=5000,
        )
        print(f'[allfeellove_auto] Edad desde seleccionada ({age_filter}): {result}')
        if not result:
            print("[allfeellove_auto] No se pudo aplicar la edad mínima; se cancela la búsqueda.")
            return

        result = self.automation.select_multiselect_option(
            ageToSelect,
            age_filter,
            search_selector=ageToInput,
            timeout=5000,
        )
        print(f'[allfeellove_auto] Edad hasta seleccionada ({age_filter}): {result}')
        if not result:
            print("[allfeellove_auto] No se pudo aplicar la edad máxima; se cancela la búsqueda.")
            return

        # El multiselect muestra una combinación de género de cuenta y preferencia.
        account_gender_label = "man" if self.account_gender in ("men", "male") else "woman"
        target_gender_label = "man" if self.target_gender in ("men", "male") else "woman"
        search_gender_label = f"I am a {account_gender_label} looking for a {target_gender_label}"
        if self.automation.element_exists(genderSelect):
            genderValue = HtmlElement.css(
                'div.ui-select[data-test-id="cmp:ui-select search-gender"] span.multiselect__single'
            )
            current_gender = self.automation.get_text(genderValue, timeout=3000)
            if current_gender and search_gender_label.lower() in current_gender.lower():
                print(f"[allfeellove_auto] Filtro de género ya coincide ({current_gender.strip()}).")
            else:
                result = self.automation.select_multiselect_option(
                    genderSelect,
                    search_gender_label,
                    timeout=5000,
                )
                print(f"[allfeellove_auto] Filtro de género seleccionado ({search_gender_label}): {result}")
                if not result:
                    print("[allfeellove_auto] No se pudo aplicar el filtro de género; se cancela la búsqueda.")
                    return

        self.automation.safe_click(searchPeople)
        print(f'[allfeellove_auto] Filtros terminados...')

        # -------------------- Sección de Buscar Perfil -------------------- #
        max_scan_pages = AutomationConfig.MAX_SCAN_PAGES
        found_profile = self._scan_profiles_until_found(self.target_profiles, max_pages=max_scan_pages)

        if found_profile:
            print(f"[allfeellove_auto] Búsqueda finalizada: '{self.last_found_profile_name}' ({self.last_found_profile_age}) localizado.")
        else:
            print(f"[allfeellove_auto] No se encontró ninguna de las opciones: {self.target_profiles} tras revisar las páginas disponibles.")

    def _normalise_text(self, value: str) -> str:
        if not value:
            return ""
        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9]+", " ", value)
        return " ".join(value.split())

    def _get_cards_data_fast(self) -> list[dict]:
        """Extrae la información de todas las tarjetas visibles en un solo viaje JS instantáneo (< 10ms)."""
        js_script = """
        () => {
            const cards = document.querySelectorAll('div.search-profile-card, [data-test-id*="file:search-item"], [data-test-id*="search-item"]');
            const results = [];
            const seen = new Set();
            let visibleIndex = 0;

            for (let i = 0; i < cards.length; i++) {
                const card = cards[i];
                if (!card || card.offsetParent === null) continue;
                const marker = `camoumacro-card-${visibleIndex++}`;
                card.setAttribute('data-camoumacro-card', marker);

                const nameEl = card.querySelector('p[data-test-id*="person-name"], p.ui-typography.color.name, p.name, .name');
                if (!nameEl) continue;

                const rawName = (nameEl.textContent || '').trim();
                if (!rawName) continue;

                const ageEl = card.querySelector('p[data-test-id*="person-display-age"], [data-test-id*="person-display-age"], p[data-test-id*="person age"], .info p');
                const rawAge = ageEl ? (ageEl.textContent || '').trim() : '';
                const ageMatch = rawAge.match(/\\d{1,3}/g);
                const age = ageMatch ? parseInt(ageMatch[ageMatch.length - 1], 10) : null;

                const cardId = card.id || card.getAttribute('data-test-id') || `card-${i}`;
                if (seen.has(cardId)) continue;
                seen.add(cardId);

                results.push({
                    index: i,
                    marker,
                    id: card.id || '',
                    testId: card.getAttribute('data-test-id') || '',
                    name: rawName,
                    age: age
                });
            }
            return results;
        }
        """
        try:
            return self.driver.page.evaluate(js_script) or []
        except Exception:
            return []

    def _scan_profile_batch_fast(self, target_profiles: dict[str, int], cards_data: list[dict]):
        """Compara las tarjetas extraídas contra el diccionario de targets en memoria de forma instantánea."""
        if not target_profiles or not cards_data:
            return None, None, None

        target_map: dict[str, tuple[str, int]] = {}
        for name, age in target_profiles.items():
            target_map[self._normalise_text(name)] = (name, age)

        for card_info in cards_data:
            name_text = self._normalise_text(card_info.get("name", ""))
            if not name_text:
                continue

            target = target_map.get(name_text)
            if target is None:
                continue

            desired_name, desired_age = target
            age_value = card_info.get("age")
            if age_value is not None and desired_age > 0 and age_value != desired_age:
                continue

            card_locator = None
            if card_info.get("marker"):
                card_locator = self.driver.page.locator(
                    f'[data-camoumacro-card="{card_info["marker"]}"]'
                ).first
                if card_locator.count() == 0:
                    card_locator = None
            if card_info.get("id"):
                card_locator = card_locator or self.driver.page.locator(f"#{card_info['id']}").first
            if card_locator is None:
                name_candidates = self.driver.page.locator(
                    'p[data-test-id*="person-name"], '
                    'p.ui-typography.color.name, p.name, .name'
                )
                for candidate_index in range(name_candidates.count()):
                    candidate = name_candidates.nth(candidate_index)
                    try:
                        candidate_name = self._normalise_text(candidate.text_content() or "")
                        if candidate_name != name_text:
                            continue
                        candidate_card = candidate.locator(
                            "xpath=ancestor::*[contains(@data-test-id,'search-item')][1]"
                        ).first
                        if candidate_card.count() > 0:
                            card_locator = candidate_card
                            break
                    except Exception:
                        continue

                if card_locator is None:
                    card_locator = self.driver.page.locator(
                        'div.search-profile-card, [data-test-id*="search-item"]'
                    ).nth(card_info["index"])

            return desired_name, desired_age, card_locator

        return None, None, None

    def _ensure_message_mode(self) -> bool:
        """Abre Mail o Chat, según el CTA disponible, y espera el campo de mensaje."""
        composer_selector = (
            'textarea[data-test-id="cmp:ui-textarea message type-your-message"], '
            'textarea#form-textarea, textarea[placeholder*="message" i], textarea'
        )
        switch_actions = [
            (
                "Mail",
                [
                    '[data-test-id*="go-to-mail"]',
                    '[data-test-id*="mail-now"]',
                    '[data-test-id*="change-to-mail"]',
                    'button:has-text("Go to mail")',
                    'button:has-text("Mail now")',
                    'button:has-text("Change to mail")',
                ],
            ),
            (
                "Chat",
                [
                    '[data-test-id*="chat-now"]',
                    'button:has-text("Chat now")',
                    '[data-test-id="cmp:ui-button click:is-chat-visible-true change-to-chat"]',
                    '[data-test-id*="change-to-chat"]',
                    'button:has-text("Change to chat")',
                ],
            ),
        ]

        for _ in range(3):
            switch_clicked = False
            for mode, selectors in switch_actions:
                for selector in selectors:
                    try:
                        action = self.driver.page.locator(selector).first
                        if action.count() > 0 and action.is_visible():
                            print(f"[allfeellove_auto] Abriendo modo {mode} con '{selector}'...")
                            action.click(force=True)
                            switch_clicked = True
                            self.driver.page.wait_for_timeout(1000)
                            break
                    except Exception:
                        continue
                if switch_clicked:
                    break

            try:
                composer = self.driver.page.locator(composer_selector).first
                composer.wait_for(state="visible", timeout=10000)
                if composer.is_visible():
                    detected_mode = mode if switch_clicked else "Mail/Chat existente"
                    print(f"[allfeellove_auto] Campo de mensaje listo ({detected_mode}).")
                    return True
            except Exception:
                pass

            self.driver.page.wait_for_timeout(300)

        return False

    def _get_message_texts(self) -> list[str]:
        message_locators = self.driver.page.locator(self.INCOMING_MESSAGE_SELECTOR)
        texts = []
        for index in range(message_locators.count()):
            content = message_locators.nth(index).locator(
                '[data-test-id="file:text-msg message"]'
            ).inner_text().strip()
            if content:
                texts.append(content)
        return texts

    def _handle_not_enough_credits(self, timeout_ms: int = 0) -> bool:
        """Wait for the low-credit modal and finish this worker cycle after 30s."""
        deadline = time.monotonic() + timeout_ms / 1000
        modal = self.driver.page.locator(self.CREDITS_MODAL_SELECTOR)
        while True:
            try:
                if modal.count() > 0 and modal.is_visible():
                    print(
                        "[allfeellove_auto][chat] Se detectó el modal de créditos "
                        "insuficientes."
                    )
                    close_button = self.driver.page.locator(
                        self.CREDITS_MODAL_CLOSE_SELECTOR
                    ).first
                    if close_button.count() > 0 and close_button.is_visible():
                        try:
                            close_button.click(timeout=5000)
                        except PlaywrightError as exc:
                            print(
                                "[allfeellove_auto][chat] No se pudo cerrar el modal; "
                                f"se cerrará al terminar este ciclo: {exc}"
                            )
                    print(
                        "[allfeellove_auto][chat] Esperando 30 segundos antes de "
                        "reiniciar el ciclo completo."
                    )
                    self.driver.page.wait_for_timeout(self.CREDITS_CYCLE_DELAY_MS)
                    return True
            except PlaywrightError as exc:
                print(
                    "[allfeellove_auto][chat] Error comprobando el modal de créditos: "
                    f"{exc}"
                )
                return False

            remaining_ms = int((deadline - time.monotonic()) * 1000)
            if remaining_ms <= 0:
                return False
            self.driver.page.wait_for_timeout(min(200, remaining_ms))

    def _send_random_sticker(self) -> bool:
        """Abre el selector, espera stickers visibles y envía uno al azar."""
        try:
            sticker_button = self.driver.page.locator(self.STICKER_BUTTON_SELECTOR).first
            if sticker_button.count() == 0 or not sticker_button.is_visible():
                print("[allfeellove_auto][sticker] Caja no disponible (posiblemente modo Mail); se omite.")
                return False

            sticker_button.click(force=True, timeout=10000)

            sticker_items = self.driver.page.locator(self.STICKER_ITEM_SELECTOR)
            deadline = time.monotonic() + 8
            sticker_count = 0
            while time.monotonic() < deadline:
                sticker_count = sticker_items.count()
                visible_items = []
                for index in range(sticker_count):
                    item = sticker_items.nth(index)
                    try:
                        if item.is_visible():
                            visible_items.append(item)
                            if len(visible_items) == 5:
                                break
                    except PlaywrightError:
                        continue

                if visible_items:
                    random.shuffle(visible_items)
                    for selected_sticker in visible_items:
                        try:
                            sticker_id = selected_sticker.get_attribute("data-test-id") or "sin-id"
                            selected_sticker.scroll_into_view_if_needed(timeout=5000)
                            selected_sticker.click(timeout=10000)
                            self.driver.page.wait_for_timeout(300)
                            print(
                                f"[allfeellove_auto][sticker] Sticker enviado: {sticker_id}; "
                                f"visibles={len(visible_items)}, encontrados={sticker_count}."
                            )
                            return True
                        except PlaywrightError as exc:
                            print(
                                f"[allfeellove_auto][sticker] No se pudo seleccionar "
                                f"{sticker_id}: {exc}"
                            )

                self.driver.page.wait_for_timeout(200)

            print(
                f"[allfeellove_auto][sticker] No se encontraron stickers visibles "
                f"tras esperar 8s; elementos coincidentes={sticker_count}."
            )
            return False
        except Exception as exc:
            print(f"[allfeellove_auto][sticker] No se pudo enviar el sticker: {exc}")
            return False

    def _wait_for_incoming_reply(
        self,
        previous_messages: list[str],
        sent_message: str,
    ) -> bool:
        """Espera hasta cinco minutos a que aparezca un mensaje entrante nuevo."""
        started_at = time.monotonic()
        deadline = time.monotonic() + self.MESSAGE_REPLY_TIMEOUT_SECONDS
        previous_counts = Counter(previous_messages)
        sent_text = sent_message.strip()
        print(
            "[allfeellove_auto][debug] Inicia espera de respuesta: "
            f"timeout={self.MESSAGE_REPLY_TIMEOUT_SECONDS}s, "
            f"selector='{self.INCOMING_MESSAGE_SELECTOR}', "
            f"mensajes previos={len(previous_messages)}, "
            f"caracteres del mensaje enviado={len(sent_text)}."
        )
        next_status_log = started_at
        while time.monotonic() < deadline:
            if self._handle_not_enough_credits():
                return False

            try:
                current_messages = self._get_message_texts()
                current_counts = Counter(current_messages)
                added_messages = current_counts - previous_counts
                sent_echo_count = min(added_messages[sent_text], 1)
                if sent_echo_count:
                    added_messages[sent_text] -= sent_echo_count
                    if added_messages[sent_text] <= 0:
                        del added_messages[sent_text]
            except Exception as exc:
                print(
                    "[allfeellove_auto][debug] Falló la lectura de mensajes "
                    f"con selector='{self.INCOMING_MESSAGE_SELECTOR}': {exc}"
                )
                return False

            elapsed = time.monotonic() - started_at
            if added_messages:
                new_message_lengths = [
                    len(text)
                    for text, occurrences in added_messages.items()
                    for _ in range(occurrences)
                ]
                print(
                    "[allfeellove_auto][debug] Respuesta detectada: "
                    f"mensajes DOM={len(current_messages)}, "
                    f"mensajes nuevos candidatos={sum(added_messages.values())}, "
                    f"longitudes={new_message_lengths}, "
                    f"eco propio excluido={sent_echo_count}, "
                    f"espera transcurrida={elapsed:.1f}s."
                )
                print("[allfeellove_auto] Respuesta entrante detectada; espera 8s antes de continuar.")
                self.driver.page.wait_for_timeout(8000)
                return True

            remaining = deadline - time.monotonic()
            if time.monotonic() >= next_status_log:
                print(
                    "[allfeellove_auto][debug] Sin respuesta todavía: "
                    f"mensajes DOM={len(current_messages)}, "
                    f"mensajes nuevos={sum(added_messages.values())}, "
                    f"eco propio excluido={sent_echo_count}, "
                    f"transcurrido={elapsed:.1f}s, restante={max(0, remaining):.1f}s."
                )
                next_status_log = time.monotonic() + 10
            self.driver.page.wait_for_timeout(min(1000, max(1, int(remaining * 1000))))

        print(
            "[allfeellove_auto][debug] Timeout esperando respuesta: "
            f"timeout={self.MESSAGE_REPLY_TIMEOUT_SECONDS}s, "
            f"transcurrido={time.monotonic() - started_at:.1f}s, "
            f"mensajes previos={len(previous_messages)}."
        )
        print("[allfeellove_auto] No llegó una respuesta dentro del límite; se detiene la secuencia para este perfil.")
        return False

    def _interact_with_found_profile(self, card_locator) -> None:
        """Interacción completa con el perfil adaptada al género objetivo."""
        view_profile_selectors = [
            'button[data-test-id="cmp:ui-button click:go-to-profile-via-button"]',
            'button[data-test-id*="go-to-profile"]',
            'a[data-test-id*="track-go-to-profile"]',
            '[data-test-id*="go-to-profile-via-button"]',
            'a.photo-card-root',
            'button:has-text("View Profile")',
        ]
        like_selectors = [
            'button[data-test-id="cmp:ui-button click:on-like"]',
            'button[data-test-id*="on-like"]',
            'button:has-text("Like")',
        ]
        wink_selectors = [
            'button[data-test-id="cmp:ui-button click:on-wink"]',
            'button[data-test-id*="on-wink"]',
            'button:has-text("Wink")',
        ]
        textarea_selector = 'textarea[data-test-id="cmp:ui-textarea message type-your-message"], textarea#form-textarea, textarea'
        send_selectors = [
            'div[data-test-id="file:add-message click:send-message"]',
            'button[data-test-id="cmp:ui-button click:send-message send"]',
            'button[data-test-id*="send-message"]',
            'button:has-text("Send")',
        ]

        # 1. Click en View Profile
        try:
            view_button = None
            for sel in view_profile_selectors:
                cand = card_locator.locator(sel).first
                if cand.count() > 0:
                    view_button = cand
                    break

            if view_button is None:
                print(
                    f"[allfeellove_auto] La tarjeta de '{self.last_found_profile_name}' "
                    "no contiene un botón View Profile."
                )
                return

            view_button.wait_for(state="visible", timeout=8000)
            view_button.click(force=True)
            print(f"[allfeellove_auto] Clic en 'View Profile' para '{self.last_found_profile_name}'.")
        except Exception as exc:
            print(f"[allfeellove_auto] No se pudo hacer clic en View Profile: {exc}")
            return

        # 2. Esperar que cargue la página del perfil
        try:
            self.driver.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.driver.page.wait_for_selector(
                'button[data-test-id*="on-like"], button[data-test-id*="on-wink"], button[data-test-id*="change-to-chat"], textarea, #mail-title',
                timeout=8000,
            )
            self.driver.page.wait_for_timeout(600)
            print(f"[allfeellove_auto] Perfil de '{self.last_found_profile_name}' cargado exitosamente.")
        except Exception:
            self.driver.page.wait_for_timeout(1000)

        # 3. Like al perfil Y Wink button
        for selector in like_selectors:
            try:
                like_btn = self.driver.page.locator(selector).first
                if like_btn.count() > 0 and like_btn.is_visible():
                    like_btn.click(force=True)
                    print(f"[allfeellove_auto] Like enviado a '{self.last_found_profile_name}'.")
                    self.driver.page.wait_for_timeout(400)
                    break
            except Exception:
                pass

        for selector in wink_selectors:
            try:
                wink_btn = self.driver.page.locator(selector).first
                if wink_btn.count() > 0 and wink_btn.is_visible():
                    wink_btn.click(force=True)
                    print(f"[allfeellove_auto] Wink enviado a '{self.last_found_profile_name}'.")
                    self.driver.page.wait_for_timeout(400)
                    break
            except Exception:
                pass

        # 4. Abrir Mail o Chat, según el CTA disponible en el perfil.
        if not self._ensure_message_mode():
            print("[allfeellove_auto] No se pudo abrir Mail/Chat o localizar el campo de mensaje; se cancela el flujo.")
            return

        # 5. Generación de diálogos adaptados al target_gender ("men" o "women")
        tone = random.choice(["flirty", "casual", "premium"])
        personality = (
            "charming, confident, and grounded"
            if self.target_gender in ("men", "male")
            else "warm, playful, and confident"
        )
        messages = PeopleTalkGenerator.build_message_set(
            count=12,
            name=self.last_found_profile_name,
            age=self.last_found_profile_age,
            personality=personality,
            tone=tone,
            target_gender=self.target_gender,
        )
        print(f"[allfeellove_auto] Generados {len(messages)} mensajes con tono '{tone}' para objetivo {self.target_gender.upper()}.")

        #Espera a que la pagina termine de abrir (8 secs)
        self.driver.page.wait_for_timeout(8000)

        for index, message in enumerate(messages, start=1):
            try:
                previous_messages = self._get_message_texts()
                print(
                    f"[allfeellove_auto][debug] Mensaje {index}/{len(messages)}: "
                    f"snapshot previo={len(previous_messages)} mensajes, "
                    f"longitud del texto a enviar={len(message)}."
                )
            except Exception as exc:
                print(f"[allfeellove_auto] No se pudo preparar la detección de respuestas: {exc}")
                break

            sent = False
            send_errors: list[str] = []
            for attempt in range(1, 4):
                try:
                    textarea = self.driver.page.locator(textarea_selector).first
                    if textarea.count() > 0:
                        textarea.wait_for(state="visible", timeout=5000)
                        textarea.click(force=True)
                        textarea.fill("")
                        textarea.fill(message)
                        self.driver.page.wait_for_timeout(300)

                        for candidate in send_selectors:
                            send_button = self.driver.page.locator(candidate).first
                            if send_button.count() == 0:
                                continue
                            try:
                                send_button.wait_for(state="visible", timeout=10000)
                                is_disabled = send_button.get_attribute("data-isdisabled") == "true"
                                if is_disabled or not send_button.is_enabled():
                                    send_errors.append(f"{candidate}: botón deshabilitado")
                                    continue
                                send_button.scroll_into_view_if_needed()
                                send_button.click(force=True, timeout=10000)
                                sent = True
                                break
                            except Exception as exc:
                                send_errors.append(f"{candidate}: {exc}")
                                continue

                        if sent:
                            print(
                                f"[allfeellove_auto][debug] Envío confirmado: "
                                f"mensaje {index}/{len(messages)}, intento={attempt}, "
                                f"botón='{candidate}', longitud={len(message)}."
                            )
                            print(f"[allfeellove_auto] Mensaje {index}/{len(messages)} enviado.")
                            break
                except Exception as exc:
                    print(
                        f"[allfeellove_auto][debug] Error enviando mensaje "
                        f"{index}/{len(messages)}, intento={attempt}: {exc}"
                    )
                    self.driver.page.wait_for_timeout(200)

            if not sent:
                print(
                    f"[allfeellove_auto] No se pudo enviar el mensaje {index}/{len(messages)}. "
                    f"Errores del botón de envío: {send_errors or ['no se encontró un botón coincidente']}."
                )
                print("[allfeellove_auto] Se pausa en este perfil para inspeccionar el botón. Cierra el navegador para continuar.")
                self.driver.wait_until_closed()
                break

            if self._handle_not_enough_credits(timeout_ms=1500):
                return

            if random.random() < self.STICKER_SEND_PROBABILITY:
                print(
                    f"[allfeellove_auto][sticker] Probabilidad activada "
                    f"para mensaje {index}/{len(messages)}."
                )
                self._send_random_sticker()
            else:
                print(
                    f"[allfeellove_auto][sticker] No se seleccionó sticker "
                    f"para mensaje {index}/{len(messages)}."
                )

            if index < len(messages):
                print("[allfeellove_auto] Esperando una respuesta (máximo 5 minutos)...")
                if not self._wait_for_incoming_reply(previous_messages, message):
                    break

    def _go_to_next_profile_page(self, current_first_id: str = "") -> bool:
        """Avanza de página rápidamente esperando de forma reactiva a que cambien las tarjetas."""
        next_page_selectors = [
            'button[data-test-id="cmp:ui-button click:change-page-options-current-page next"]',
            'button[data-test-id*="change-page-options-current-page next"]',
            '[data-test-id="cmp:ui-button click:change-page-options-current-page next"]',
            'button:has-text("Next")',
        ]

        for selector in next_page_selectors:
            try:
                candidate = self.driver.page.locator(selector).first
                if candidate.count() > 0 and candidate.is_visible():
                    candidate.click(force=True)

                    deadline = time.monotonic() + 1.5
                    while time.monotonic() < deadline:
                        self.driver.page.wait_for_timeout(60)
                        cards = self._get_cards_data_fast()
                        if cards:
                            new_id = cards[0].get("id") or cards[0].get("name")
                            if new_id and new_id != current_first_id:
                                return True
                    return True
            except Exception:
                continue

        return False

    def _scroll_to_next_profile_view(self) -> tuple[bool, bool, dict]:
        """Desplaza el contenedor real de resultados y devuelve sus métricas."""
        try:
            state = self.driver.page.evaluate(
                """
                () => {
                    const card = document.querySelector(
                        'div.search-profile-card, [data-test-id*="file:search-item"], [data-test-id*="search-item"]'
                    );
                    const root = document.scrollingElement || document.documentElement;
                    let container = root;
                    let node = card;

                    while (node && node !== document.body) {
                        const style = getComputedStyle(node);
                        if (node.scrollHeight > node.clientHeight + 12 &&
                            (style.overflowY === 'auto' || style.overflowY === 'scroll')) {
                            container = node;
                            break;
                        }
                        node = node.parentElement;
                    }

                    const before = container.scrollTop;
                    const viewportHeight = container === root ? window.innerHeight : container.clientHeight;
                    const step = Math.max(180, Math.floor(viewportHeight * 0.75));
                    container.scrollBy({top: step, behavior: 'auto'});
                    const after = container.scrollTop;
                    const maxScroll = Math.max(0, container.scrollHeight - viewportHeight);
                    const loading = [...document.querySelectorAll(
                        'div.search-profile-card, [data-test-id*="file:search-item"], [data-test-id*="search-item"]'
                    )].filter((item) => {
                        const style = getComputedStyle(item);
                        return style.backgroundColor === 'rgb(255, 255, 255)' ||
                            item.classList.contains('loading') ||
                            item.getAttribute('aria-busy') === 'true';
                    }).length;
                    return {
                        before,
                        after,
                        maxScroll,
                        bottom: after >= maxScroll - 8,
                        height: container.scrollHeight,
                        loading,
                        container: container === root ? 'document' : (container.className || container.tagName)
                    };
                }
                """
            )
            advanced = state and state.get("after", 0) > state.get("before", 0)
            return bool(advanced), bool(state and state.get("bottom")), state or {}
        except Exception as exc:
            print(f"[allfeellove_auto] No se pudo desplazar a la siguiente vista: {exc}")
            return False, False, {}

    def _wait_for_new_profile_view(self, previous_signature: tuple[str, ...], timeout_ms: int = 1200) -> list[dict]:
        """Espera tarjetas nuevas tras un scroll, tolerando el lazy loading."""
        deadline = time.monotonic() + timeout_ms / 1000
        latest_cards: list[dict] = []
        while time.monotonic() < deadline:
            latest_cards = self._get_cards_data_fast()
            current_signature = tuple(
                f"{self._normalise_text(card.get('name', ''))}:{card.get('age')}"
                for card in latest_cards
            )
            if current_signature and current_signature != previous_signature:
                return latest_cards
            self.driver.page.wait_for_timeout(100)
        return latest_cards

    def _scan_profiles_until_found(self, target_profiles: dict[str, int], max_pages: int = 25) -> bool:
        """Escanea resultados por vistas verticales, esperando tarjetas lazy-loaded."""
        scanned_profiles: set[tuple[str, int | None]] = set()
        previous_signature: tuple[str, ...] = ()
        stalled_views = 0

        for _ in range(1, max_pages + 1):
            cards_data = self._wait_for_new_profile_view(previous_signature, timeout_ms=1200)
            current_signature = tuple(
                f"{self._normalise_text(card.get('name', ''))}:{card.get('age')}"
                for card in cards_data
            )
            new_cards = []
            for card in cards_data:
                profile_key = (self._normalise_text(card.get("name", "")), card.get("age"))
                if profile_key not in scanned_profiles:
                    scanned_profiles.add(profile_key)
                    new_cards.append(card)

            names = [card.get("name", "") for card in new_cards]
            if names:
                print(f"[allfeellove_auto] Personas escaneadas: {', '.join(names)}")

            matched_name, matched_age, matched_card = self._scan_profile_batch_fast(target_profiles, new_cards)
            if matched_card is not None:
                self.last_found_profile_name = matched_name
                self.last_found_profile_age = matched_age
                print(f"[allfeellove_auto] Objetivo encontrado: '{matched_name}' ({matched_age}).")
                try:
                    self._interact_with_found_profile(matched_card)
                except Exception:
                    print(f"[allfeellove_auto] El perfil fue localizado, pero falló la interacción con '{matched_name}'.")
                return True

            advanced, at_bottom, scroll_state = self._scroll_to_next_profile_view()
            if advanced:
                stalled_views = 0
                previous_signature = current_signature
                self.driver.page.wait_for_timeout(60)
                continue

            stalled_views += 1
            self.driver.page.wait_for_timeout(700 if scroll_state.get("loading", 0) else 250)
            previous_signature = current_signature
            if at_bottom and stalled_views >= 3:
                print("[allfeellove_auto] Se alcanzó el final y no aparecen más tarjetas.")
                return False

        return False


def run_allfeellove_auto(
    driver: CamoufoxHandler,
    account_gender: str | None = None,
    target_gender: str | None = None,
    targets_file: str | Path | None = None,
) -> None:
    """Wrapper para ejecutar el algoritmo Allfeellove Auto."""
    algorithm = AllfeelloveAuto(
        driver,
        account_gender=account_gender,
        target_gender=target_gender,
        targets_file=targets_file,
    )
    algorithm.run()
