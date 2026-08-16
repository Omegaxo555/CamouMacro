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

            for (let i = 0; i < cards.length; i++) {
                const card = cards[i];
                if (!card || card.offsetParent === null) continue;

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
            if age_value is not None and age_value != desired_age:
                continue

            card_locator = None
            if card_info.get("id"):
                card_locator = self.driver.page.locator(f"#{card_info['id']}").first
            elif card_info.get("testId"):
                card_locator = self.driver.page.locator(f'[data-test-id="{card_info["testId"]}"]').first
            else:
                card_locator = self.driver.page.locator('div.search-profile-card, [data-test-id*="search-item"]').nth(card_info["index"])

            return desired_name, desired_age, card_locator

        return None, None, None

    def _ensure_chat_mode(self) -> bool:
        """Verifica si la vista está en Mail o Chat y cambia a Chat si es necesario."""
        textarea_selector = 'textarea[data-test-id="cmp:ui-textarea message type-your-message"], textarea#form-textarea, textarea[placeholder*="message" i]'
        switch_selectors = [
            'button[data-test-id="cmp:ui-button click:is-chat-visible-true change-to-chat"]',
            'button[data-test-id*="change-to-chat"]',
            'button:has-text("Change to chat")',
            '.x8gxgoBU button',
            '#mail-title ~ button',
        ]

        for _ in range(3):
            # 1. Comprobar si ya está en modo Chat (textarea visible)
            try:
                textarea = self.driver.page.locator(textarea_selector).first
                if textarea.count() > 0 and textarea.is_visible():
                    print("[allfeellove_auto] Modo Chat ya está activo.")
                    return True
            except Exception:
                pass

            # 2. Buscar y presionar el botón 'Change to chat'
            for selector in switch_selectors:
                try:
                    button = self.driver.page.locator(selector).first
                    if button.count() > 0 and button.is_visible():
                        print("[allfeellove_auto] Detectado modo Mail. Cambiando a Chat...")
                        button.click(force=True)
                        self.driver.page.wait_for_timeout(600)
                        break
                except Exception:
                    pass

            # 3. Esperar que aparezca el textarea de chat
            try:
                textarea = self.driver.page.locator(textarea_selector).first
                textarea.wait_for(state="visible", timeout=3000)
                if textarea.is_visible():
                    print("[allfeellove_auto] Modo Chat activado exitosamente.")
                    return True
            except Exception:
                pass

            self.driver.page.wait_for_timeout(300)

        return False

    def _send_sticker_batch(self, sticker_count: int = 5) -> None:
        """Abre la interfaz de stickers y envía la cantidad indicada (por defecto 5)."""
        toggle_selectors = [
            'button[data-test-id="click:toggle-sticker-box"]',
            'button[data-test-id*="toggle-sticker"]',
            'button[data-test-id*="sticker"]',
            'button:has-text("Stickers")',
        ]
        sticker_selector = 'div[data-test-id*="click:on-send-sticker-sticker"], div[data-test-id*="on-send-sticker"], .sticker-item, img[data-test-id*="sticker"]'

        opened = False
        for selector in toggle_selectors:
            try:
                toggle_button = self.driver.page.locator(selector).first
                if toggle_button.count() > 0:
                    toggle_button.wait_for(state="visible", timeout=5000)
                    toggle_button.scroll_into_view_if_needed()
                    toggle_button.click(force=True)
                    opened = True
                    self.driver.page.wait_for_timeout(500)
                    break
            except Exception:
                pass

        if not opened:
            print("[allfeellove_auto] No se encontró el botón para abrir stickers.")
            return

        try:
            sticker_items = self.driver.page.locator(sticker_selector)
            self.driver.page.wait_for_timeout(400)
            total_items = sticker_items.count()
            if total_items == 0:
                print("[allfeellove_auto] No hay stickers visibles en la caja.")
                return

            target_count = sticker_count
            for index in range(target_count):
                item_idx = index % total_items
                item = sticker_items.nth(item_idx)
                try:
                    item.wait_for(state="visible", timeout=3000)
                    item.scroll_into_view_if_needed()
                    item.click(force=True)
                    print(f"[allfeellove_auto] Sticker {index + 1}/{target_count} enviado.")
                    self.driver.page.wait_for_timeout(400)
                except Exception:
                    continue
            print(f"[allfeellove_auto] Proceso de stickers completado ({target_count} enviados).")
        except Exception as exc:
            print(f"[allfeellove_auto] Error al enviar stickers: {exc}")

    def _interact_with_found_profile(self, card_locator) -> None:
        """Interacción completa con el perfil: View Profile -> Like & Wink -> Chat mode -> Mensajes -> Stickers."""
        view_profile_selectors = [
            'button[data-test-id="cmp:ui-button click:go-to-profile-via-button"]',
            'button[data-test-id*="go-to-profile"]',
            'a[data-test-id*="track-go-to-profile"]',
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
                view_button = self.driver.page.locator(view_profile_selectors[0]).first

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
                timeout=8000
            )
            self.driver.page.wait_for_timeout(600)
            print(f"[allfeellove_auto] Perfil de '{self.last_found_profile_name}' cargado exitosamente.")
        except Exception:
            self.driver.page.wait_for_timeout(1000)

        # 3. Like al perfil Y Wink button
        # Like
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

        # Wink
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

        # 4. Verificar modo Mail y cambiar a Chat si es necesario
        if not self._ensure_chat_mode():
            print("[allfeellove_auto] El modo Chat no se pudo activar; se cancela el flujo de mensajes.")
            return

        # 5. Escribir muy rápido los mensajes generados y enviar cada uno con cooldown de 2.5s
        tone = random.choice(["flirty", "casual", "premium"])
        messages = PeopleTalkGenerator.build_message_set(
            count=4,
            name=self.last_found_profile_name,
            age=self.last_found_profile_age,
            personality="warm, playful, and confident",
            tone=tone,
        )

        for index, message in enumerate(messages, start=1):
            sent = False
            for _ in range(3):
                try:
                    textarea = self.driver.page.locator(textarea_selector).first
                    if textarea.count() > 0:
                        textarea.wait_for(state="visible", timeout=5000)
                        textarea.click(force=True)
                        textarea.fill("")
                        textarea.fill(message)
                        self.driver.page.wait_for_timeout(50)

                        for candidate in send_selectors:
                            send_button = self.driver.page.locator(candidate).first
                            if send_button.count() > 0 and send_button.is_visible():
                                send_button.click(force=True)
                                sent = True
                                break

                        if sent:
                            print(f"[allfeellove_auto] Mensaje {index}/{len(messages)} enviado: '{message}'")
                            break
                except Exception as exc:
                    print(f"[allfeellove_auto] Reintento de mensaje {index}/{len(messages)}: {exc}")
                    self.driver.page.wait_for_timeout(200)

            if not sent:
                print(f"[allfeellove_auto] No se pudo enviar el mensaje {index}/{len(messages)}.")
                break

            # Cooldown obligatorio de 2.5s entre mensajes
            if index < len(messages):
                print("[allfeellove_auto] Esperando cooldown de 2.5s...")
                self.driver.page.wait_for_timeout(2500)

        # 6. Abrir la interfaz de stickers y enviar 5 stickers
        self.driver.page.wait_for_timeout(500)
        try:
            self._send_sticker_batch(sticker_count=5)
        except Exception as exc:
            print(f"[allfeellove_auto] Error al enviar stickers: {exc}")

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

                    # Espera reactiva: verifica cada 60ms si las tarjetas cambiaron (máx 1.5s)
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

    def _scan_profiles_until_found(self, target_profiles: dict[str, int], max_pages: int = 25) -> bool:
        """Búsqueda ultra rápida de perfiles a través de las páginas."""
        for page_index in range(1, max_pages + 1):
            # 1. Espera rápida a que haya tarjetas visibles (máx 1.5s, usualmente < 80ms)
            cards_data = []
            deadline = time.monotonic() + 1.5
            while time.monotonic() < deadline:
                cards_data = self._get_cards_data_fast()
                if cards_data:
                    break
                self.driver.page.wait_for_timeout(50)

            visible_names = [c["name"] for c in cards_data]
            print(f"[allfeellove_auto] Página {page_index}. Nombres visibles: {visible_names[:12]}")

            # 2. Búsqueda instantánea en memoria (0 ms)
            matched_name, matched_age, matched_card = self._scan_profile_batch_fast(target_profiles, cards_data)

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

            # 3. Si no se encontró en esta página, avanzar de inmediato
            first_id = cards_data[0].get("id") or (cards_data[0].get("name") if cards_data else "")
            print(f"[allfeellove_auto] Ninguno de {target_profiles} fue encontrado. Avanzando con Next...")
            if not self._go_to_next_profile_page(current_first_id=first_id):
                print(f"[allfeellove_auto] El botón Next no está disponible. Se terminó la búsqueda.")
                return False

        return False


def run_allfeellove_auto(driver: CamoufoxHandler) -> None:
    """Wrapper para ejecutar el algoritmo personalizado."""
    algorithm = AllfeelloveAuto(driver)
    algorithm.run()
