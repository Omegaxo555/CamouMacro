"""
main.py
"""

from core.camoufox_driver import CamoufoxDriver
from modules.form_automator import FormAutomator

def main():
    # Asignar la plantilla de perfil persistente (si existe)
    PLANTILLA_PERFIL = "templates/perfil_base.tar.gz"

    driver = CamoufoxDriver(
        proxy_server="socks5://127.0.0.1:9050",
        profile_template=PLANTILLA_PERFIL,  # Extrae en /tmp y limpia al cerrar
        headless=False
    )

    try:
        if not driver.initialize():
            print("[-] Error al inicializar el driver.")
            return

        if driver.navigate("https://httpbin.org/forms/post"):
            automator = FormAutomator(driver.page)
            
            # Flujo de trabajo automatizado...
            automator.human_type("input[name='custname']", "Alex Ruiz")

    finally:
        # Se ejecuta siempre, garantizando que /tmp/camoufox_session_* sea borrado
        driver.close()

if __name__ == "__main__":
    main()