"""Módulo base para construir el algoritmo Allfeellove Auto."""

from __future__ import annotations
import random
import traceback

from core.camoufox_handler import CamoufoxHandler
from modules.browser_automation import BrowserAutomation, HtmlElement
from modules.InfoGeneration.peopleInfo_generator import PeopleInfoGenerator


class AllfeelloveAuto:
    """Estructura base para tu algoritmo personalizado."""

    def __init__(self, driver: CamoufoxHandler):
        self.driver = driver
        self.automation = BrowserAutomation(driver.page) if driver.page else None

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

        result = self.automation.safe_click(signup_button)
        result = self.automation.safe_click(signup_button)
        print(f"[allfeellove_auto] Verificando existencia de botón de signup: {result}")

        #--------Saltando a la reclamar los credits-------#

        print('[allfeellove_auto] Esperando por inicio de sesion')

        nextLets_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:next Let’s do it!"]')
        nextStep_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:skip skip"]')
        nextStep2_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:pref-gender female"]')
        nextStep3_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:skip skip"]')
        nextStep4_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:onSkip Skip"]')
        nextStep5_button = HtmlElement.css('button[data-test-id="cmp:ui-button click:next Continue"]')
        

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



def run_allfeellove_auto(driver: CamoufoxHandler) -> None:
    """Wrapper para ejecutar el algoritmo personalizado."""
    algorithm = AllfeelloveAuto(driver)
    algorithm.run()
