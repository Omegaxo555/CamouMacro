import sys
import logging
import platform
import shutil
import socket
import tarfile
import tempfile
from pathlib import Path
from typing import Optional
from camoufox.sync_api import Camoufox
from playwright.sync_api import Error as PlaywrightError, Page, BrowserContext

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


class CamoufoxHandler:
    def __init__(
        self,
        proxy_server: Optional[str] = None,
        tor_proxy: Optional[str] = None,
        profile_template: Optional[str] = None,
        headless: bool = True,
        timeout: int = 30000,
        window_size: Optional[tuple[int, int]] = (560, 420),
        tor_ports: Optional[list[int]] = None,
    ):

        resolved_proxy = proxy_server or tor_proxy or "socks5://127.0.0.1:9050"
        self.proxy_server = resolved_proxy
        self.tor_proxy = resolved_proxy
        self.profile_template = profile_template
        self.headless = headless
        self.timeout = timeout
        self.window_size = window_size or (560, 420)
        self.tor_ports = tor_ports or [9050, 9150, 9051, 9052]
        self._tor_port_index = 0

        self.browser_context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.temp_dir: Optional[Path] = None
        self._camoufox_cm = None
        self._camoufox_instance = None

    def _build_tor_proxy_for_port(self, port: int) -> str:
        return f"socks5://127.0.0.1:{port}"

    def _next_tor_proxy(self) -> str:
        port = self.tor_ports[self._tor_port_index % len(self.tor_ports)]
        self._tor_port_index += 1
        return self._build_tor_proxy_for_port(port)

    def _check_page_blocked_by_cloudflare(self) -> bool:
        if not self.page:
            return False

        try:
            current_url = (self.page.url or "").lower()
            if "cloudflare" in current_url or "attention required" in current_url:
                return True

            body_text = self.page.locator("body").inner_text(timeout=3000)
            body_lower = (body_text or "").lower()
            markers = [
                "attention required",
                "sorry, you have been blocked",
                "verify you are human",
                "cloudflare ray id",
                "checking your browser before accessing",
                "just a moment",
            ]
            return any(marker in body_lower for marker in markers)
        except Exception:
            return False

    def is_cloudflare_blocked(self) -> bool:
        """Devuelve True si la página actual es la pantalla de bloqueo de Cloudflare."""
        return self._check_page_blocked_by_cloudflare()

    def rotate_connection(self, use_tor: bool = True, custom_proxy: Optional[str] = None) -> bool:
        """Cierra la sesión actual y reinicia el navegador con una salida nueva. Si usa Tor, prueba otro puerto; si no, usa proxy_server/custom_proxy."""
        logging.warning("Reiniciando navegador para cambiar salida de red y evitar bloqueo por Cloudflare...")
        self.close()

        if custom_proxy:
            self.proxy_server = custom_proxy
        elif use_tor:
            self.tor_proxy = self._next_tor_proxy()
            self.proxy_server = self.tor_proxy

        return self.initialize()

    def try_refresh_after_cloudflare_block(self, max_retries: int = 3) -> bool:
        """Intenta navegar con rotación de salida si detecta bloqueo de Cloudflare."""
        for attempt in range(1, max_retries + 1):
            if self.page is not None and self._check_page_blocked_by_cloudflare():
                logging.warning(f"Cloudflare bloqueó la página. Reiniciando conexión ({attempt}/{max_retries})...")
                if not self.rotate_connection(use_tor=True):
                    logging.error("No se pudo reiniciar la sesión del navegador.")
                    return False
                continue
            return True
        return True
    
    def _prepare_profile(self) -> Optional[str]:
        if not self.profile_template:
            logging.info("No se proporcionó una plantilla de perfil. Se utilizará el perfil predeterminado de Camoufox.")
            return None

        archive_path = Path(self.profile_template)
        if not archive_path.is_file():
            logging.warning(f"La plantilla de perfil no existe: {self.profile_template}. Intentando generarla automáticamente...")
            try:
                from generate_profile_template import build_profile_template
                archive_path = Path(build_profile_template())
            except Exception as exc:
                logging.error(f"No se pudo crear la plantilla de perfil automática: {exc}")
                raise FileNotFoundError(f"el archivo de plantilla de perfil no existe: {self.profile_template}") from exc

        self.temp_dir = Path(tempfile.mkdtemp(prefix="camoufox_session_", dir="/tmp"))
        logging.info(f"Extrayendo plantilla de perfil a: {self.temp_dir}")

        logging.info(f"Extrayendo plantilla de perfil desde: {archive_path.name} en memoria")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=self.temp_dir)

        return str(self.temp_dir)

    @staticmethod
    def is_tor_available(host: str = "127.0.0.1", port: int = 9050) -> bool:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            sock.connect((host, port))
            return True
        except OSError:
            return False
        finally:
            sock.close()

    def initialize(self) -> bool:
        """
        Inicializa la sesión de Camoufox con el perfil preparado en RAM
        y la configuración de red Tor solo si está disponible.
        """
        if self._camoufox_instance is not None and self.page is not None:
            logging.info("La sesión del navegador ya está inicializada. Se reutiliza la instancia actual.")
            return True

        try:
            user_data_path = self._prepare_profile()

            tor_available = self.is_tor_available()
            if tor_available:
                logging.info("Inicializando motor Camoufox sobre Tor...")
            else:
                logging.warning("Tor no está disponible en 127.0.0.1:9050. Iniciando Camoufox sin proxy.")

            camoufox_kwargs = {
                "headless": self.headless,
                "humanize": True,
                "os": "windows" if platform.system() == "Windows" else "linux",
                "geoip": tor_available,
                "window": self.window_size,
            }

            if tor_available and self.proxy_server:
                camoufox_kwargs["proxy"] = {"server": self.proxy_server}

            if user_data_path:
                camoufox_kwargs["persistent_context"] = True
                camoufox_kwargs["user_data_dir"] = user_data_path

            self._camoufox_instance = Camoufox(**camoufox_kwargs)
            context = self._camoufox_instance.__enter__()
            self.browser_context = context

            try:
                self.browser_context.grant_permissions(["notifications"], origin="https://allfeellove.com")
                logging.info("Permisos de notificaciones bloqueados para https://allfeellove.com")
            except Exception as exc:
                logging.warning(f"No se pudieron bloquear notificaciones en el contexto: {exc}")

            if hasattr(context, "pages"):
                pages = getattr(context, "pages")
                if pages:
                    self.page = pages[0]
                else:
                    self.page = context.new_page()
            elif hasattr(context, "new_page"):
                self.page = context.new_page()
            else:
                self.page = context

            if self.page is not None:
                self.page.set_default_timeout(self.timeout)

            logging.info("CamoufoxDriver inicializado exitosamente.")
            logging.info(f"Timeout por defecto del navegador: {self.timeout}ms")
            logging.info(f"Ventana flotante configurada en {self.window_size[0]}x{self.window_size[1]}.")
            return True

        except PlaywrightError as e:
            logging.error(f"Error de Playwright durante la inicialización: {e}")
            self.close()
            return False
        except Exception as e:
            logging.error(f"Error inesperado al preparar el Driver: {e}")
            self.close()
            return False


    def navigate(self, url: str, max_retries: int = 3) -> bool:
        """Navega a la URL especificada con tolerancia a fallos de latencia."""
        if not self.page:
            logging.error("Página no inicializada. Llame a initialize() primero.")
            return False

        for attempt in range(1, max_retries + 1):
            try:
                logging.info(f"Navegando a {url} (Intento {attempt}/{max_retries})...")
                response = self.page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)

                if response and response.ok:
                    logging.info(f"Página cargada con éxito: {url} [{response.status}]")
                    if self._check_page_blocked_by_cloudflare():
                        logging.warning("La página respondió con bloqueo de Cloudflare. Se intentará rotar la salida de red.")
                        if not self.rotate_connection(use_tor=True):
                            logging.error("No se pudo cambiar la salida de red para evitar Cloudflare.")
                            return False
                        if not self.page:
                            return False
                        response = self.page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
                        if response and response.ok and not self._check_page_blocked_by_cloudflare():
                            return True
                    return True

                status = response.status if response else "Sin Respuesta"
                logging.warning(f"Estado de respuesta no óptimo: {status}")

            except PlaywrightError as e:
                logging.warning(f"Error temporal de red en el intento {attempt}: {e}")

        logging.error(f"Imposible conectar a {url} tras {max_retries} intentos.")
        return False

    def close(self) -> None:
        """
        Cierra el navegador y garantiza la eliminación total del perfil
        temporal almacenado en /tmp.
        """
        logging.info("Iniciando proceso de cierre y limpieza...")
        
        # 1. Cerrar la instancia del navegador
        if self._camoufox_instance:
            try:
                self._camoufox_instance.__exit__(None, None, None)
                self._camoufox_instance = None
                logging.info("Instancia del navegador cerrada.")
            except Exception as e:
                logging.error(f"Error al cerrar la sesión de Camoufox: {e}")

        self.browser_context = None
        self.page = None

        # 2. Borrar permanentemente el directorio temporal en RAM
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                logging.info(f"Limpieza completada. Perfil efímero borrado de {self.temp_dir}")
                self.temp_dir = None
            except Exception as e:
                logging.error(f"Error al eliminar el directorio temporal {self.temp_dir}: {e}")
    
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
