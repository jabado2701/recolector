import time
import json
import os
from time import sleep

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import unicodedata
import re


def setup_chromedriver():
    """Verifica o descarga ChromeDriver y devuelve su ruta."""
    print("🔄 Verificando instalación de ChromeDriver (una vez)...")
    driver_path = obtener_ruta_driver(force_download=True)
    print("✅ ChromeDriver verificado.")
    return driver_path


def leer_cookies(ruta_cookies="Insertar ruta al archivo JSON con las cookies de X/Twitter"):
    """Lee el archivo cookies.json y devuelve una lista de conjuntos de cookies."""
    with open(ruta_cookies, "r") as file:
        cookies = json.load(file)
    return cookies


def obtener_ruta_driver(force_download=False):
    """Devuelve la ruta del ChromeDriver ya descargado o lo descarga si se fuerza."""
    if not force_download:
        base_dir = os.path.expanduser("~\\AppData\\Roaming\\undetected_chromedriver\\undetected\\chromedriver-win32")
        return os.path.join(base_dir, "chromedriver.exe")

    driver = uc.Chrome(headless=True, version_main=138)
    driver_path = driver.patcher.executable_path
    driver.quit()
    return driver_path


def get_chrome_driver(process_id, driver_path, headless=True):
    """Inicializa ChromeDriver usando el path ya descargado."""
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1280,1024")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    if headless:
        options.add_argument("--headless=new")

    driver = uc.Chrome(options=options, driver_executable_path=driver_path)
    print(f"✅ ChromeDriver iniciado en el proceso {process_id}")
    sleep(3)
    return driver


def cargar_cookies(driver, cookies):
    """Carga un conjunto específico de cookies en el navegador."""
    try:
        driver.get("https://x.com")
        time.sleep(3)

        for cookie in cookies["cookies"]:
            driver.add_cookie(cookie)

        driver.refresh()

        print(f"✅ Cookies cargadas correctamente para ID {cookies['id']}")
    except Exception as e:
        print(f"⚠️ No se pudieron cargar las cookies para ID {cookies['id']}: {e}")


def convertir_numero_abreviado(texto):
    if not texto:
        return 0

    texto = texto.strip().lower().replace(',', '.')
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')

    try:
        if 'm' in texto:
            num = float(re.findall(r"[\d.]+", texto)[0])
            return int(num * 1_000_000)
        elif 'mil' in texto:
            num = float(re.findall(r"[\d.]+", texto)[0])
            return int(num * 1_000)
        elif 'k' in texto:
            num = float(re.findall(r"[\d.]+", texto)[0])
            return int(num * 1_000)
        else:
            return int(texto)
    except:
        return 0


def extraer_metricas_tweet(tweet):
    try:
        metricas = tweet.find_elements(By.XPATH,
                                       './/button[@data-testid="like"] | .//button[@data-testid="retweet"] | .//button[@data-testid="reply"]')
        likes = retweets = comentarios = 0

        for metrica in metricas:
            try:
                aria_label = metrica.get_attribute("aria-label")
                if not aria_label:
                    print("No hay aria-label")
                    continue

                aria_label_lower = aria_label.lower()
                numero_str = aria_label.split()[0]

                if "me gusta" in aria_label_lower or "like" in aria_label_lower:
                    likes = convertir_numero_abreviado(numero_str)
                elif "retweet" in aria_label_lower or "repost" in aria_label_lower or "repostear" in aria_label_lower:
                    retweets = convertir_numero_abreviado(numero_str)
                elif "respuesta" in aria_label_lower or "respuestas" in aria_label_lower or "reply" in aria_label_lower or "replies" in aria_label_lower:
                    comentarios = convertir_numero_abreviado(numero_str)
            except Exception as e:
                print("Error procesando métrica:", e)
                continue

        return comentarios, retweets, likes
    except Exception as e:
        print("Error general:", e)
        return 0, 0, 0
