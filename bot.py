import sys 
import logging
from typing import Optional
from camoufox.sync_api import Camoufox
from playwright.async_api import error as PlaywrightError, Page, BrowserContext

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


class CamoufoxBot:
    def __init__(
        self,
        api_key: str, 
        context: Optional[BrowserContext] = None,
        tor_proxy: str = "socks5://127.0.0.1:9050",
        headless: bool = True,
        timeout: int = 30
        ):
        self.api_key = api_key
        self.context = context
        self.tor_proxy = tor_proxy
        self.headless = headless
        self.timeout = timeout
        self.browser_context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._camoufox_cm = None
    
    def start(self) -> bool:
        try:
            logging.info("Starting CamoufoxBot...")


            #Inicializador de contexto de navegador
            self._camoufox_cm = Camoufox(
                proxy={"server": self.tor_proxy},
                headless=self.headless,
                humanize=True,
                os="lin"
            )

            self.page = self._camoufox_cm.__enter__()
            self.page.set_default_timeout(self.timeout * 1000)  # Convert seconds to milliseconds

            logging.info("CamoufoxBot started successfully.")
            return True
        except PlaywrightError as e:
            logging.error(f"Failed to start CamoufoxBot: {e}")
            return False

        except Exception as e:
            logging.error(f"Unexpected error occurred while starting CamoufoxBot: {e}")
            return False


    def navigate(self, url: str, max_retries: int = 5) -> bool:
        if not self.page:
            logging.error("Page is not initialized. Call start() before navigating.")
            return False

        for attempt in range(max_retries):
            try: 
                logging.info(f"Intentando navegar a {url} (Intento {attempt}/{max_retries})...")

                #domcontentloaded permite continuar en cuanto el html cargue
                response = self.page.goto(url, wait_until="domcontentloaded")

                if (response and response.ok):
                    logging.info(f"Navegación exitosa a {url}.")
                    return True
                else:
                    status = response.status if response else "No response"
                    logging.warning(f"Failed to navigate to {url} (Intento {attempt}/{max_retries}). Status: {status}")

            except PlaywrightError as e:
                logging.error(f"Playwright error while navigating to {url} (Intento {attempt}/{max_retries}): {e}")
        
        logging.error(f"Failed to navigate to {url} after {max_retries} attempts.")
        return False

    
    def verify_ip(self) -> None:
        if not self.page:
            logging.error("Page is not initialized. Call start() before verifying IP.")
            return

        try:
            logging.info("Verificando dirección IP...")
            self.page.goto("https://check.torproject.org/", wait_until="domcontentloaded")
            
            # Verificación del mensaje oficial de Tor
            is_tor = self.page.is_visible("text=Congratulations. This browser is configured to use Tor.")
            if is_tor:
                logging.info("[CONFIRMADO] La conexión está circulando a través de la red Tor.")
            else:
                logging.warning("[ALERTA] La página cargó pero no confirmó la red Tor.")
        except Exception as e:
            logging.error(f"No se pudo verificar la IP en Tor Project: {e}")

    def stop(self) -> None:
        """
        Cierra de forma segura la sesión del navegador liberando recursos.
        """
        logging.info("Cerrando instancia de navegador y liberando recursos...")
        if self._camoufox_cm:
            try:
                self._camoufox_cm.__exit__(None, None, None)
                logging.info("Sesión cerrada correctamente.")
            except Exception as e:
                logging.error(f"Error al cerrar la sesión de Camoufox: {e}")
