import time
import json
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager


def crear_driver(headless: bool = True) -> WebDriver:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def cargar_cookies(driver: WebDriver, cookies: List[dict]):
    for cookie in cookies:
        driver.add_cookie({
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie.get("domain", ".x.com"),
            "path": "/"
        })


def obtener_cookies_desde_archivo(path: str) -> List[dict]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data[0]["cookies"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"❌ Error cargando cookies: {e}")
        return []


def extraer_html_cronologia(url: str,
                            archivo_salida: str = 'cronologia.html',
                            cookies_path: str = 'Insertar ruta al archivo JSON con las cookies de X/Twitter',
                            headless: bool = True):
    """
    Extrae el HTML del div de cronología desde un perfil de Twitter/X.
    """
    driver = crear_driver(headless=headless)

    try:
        driver.get("https://x.com")
        time.sleep(2)

        cookies = obtener_cookies_desde_archivo(cookies_path)
        if not cookies:
            print("⚠️ No se pudieron cargar cookies. Abortando.")
            return

        cargar_cookies(driver, cookies)
        time.sleep(1)

        driver.get(url)
        time.sleep(5)

        elementos = driver.find_elements(By.XPATH, "//div[contains(@aria-label, 'Cronología: Posts de')]")
        if elementos:
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                f.write(elementos[0].get_attribute('outerHTML'))
            print(f'✅ HTML guardado en: {archivo_salida}')
        else:
            print("⚠️ No se encontró el contenido de 'Cronología: Posts de'.")

    finally:
        driver.quit()


if __name__ == "__main__":
    extraer_html_cronologia("https://x.com/JuanMa_Moreno")
