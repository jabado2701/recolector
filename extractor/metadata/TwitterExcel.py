import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import pandas as pd
import re
import os
import json


def convert_to_number(text):
    if isinstance(text, str):
        text = text.replace('.', '').replace(',', '.')
        if 'mil' in text.lower():
            return int(float(text.lower().replace('mil', '').strip()) * 1_000)
        elif 'm' in text.lower():
            return int(float(text.lower().replace('m', '').strip()) * 1_000_000)
        try:
            return int(float(text))
        except ValueError:
            return "N/A"
    return "N/A"


def cargar_cookies(driver, cookies_path):
    try:
        with open(cookies_path, "r") as file:
            cookies = json.load(file)
            cookies = cookies[0]['cookies']

        driver.get("https://x.com")
        time.sleep(3)

        for cookie in cookies:
            driver.add_cookie(cookie)

        driver.refresh()
        time.sleep(3)
        print("✅ Cookies cargadas correctamente. Sesión iniciada.")
    except Exception as e:
        print(f"⚠️ No se pudieron cargar las cookies: {e}")


file_path = "Insertar ruta al archivo Excel"
cookies_path = "Insertar ruta al archivo JSON con las cookies de X/Twitter"

if not os.path.exists(file_path):
    print("⚠️ No se encontró el archivo Excel. Verifica la ruta.")
    exit()

all_sheets = pd.read_excel(file_path, sheet_name=None)

sheet_name = 'Metadata'
if sheet_name not in all_sheets:
    print("⚠️ No se encontró la hoja Metadata.")
    exit()

df = all_sheets[sheet_name]
df["Comienzo en X/Twitter"] = df["Comienzo en X/Twitter"].astype("object")
df["Descripción"] = df["Descripción"].astype("object")

for col in ["Posts", "Seguidores", "Comienzo en X/Twitter", "Descripción"]:
    if col not in df.columns:
        df[col] = ""

options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
options.add_argument("--headless")

driver = uc.Chrome(options=options)
cargar_cookies(driver, cookies_path)

try:
    cambios_realizados = False

    for index, row in df.iterrows():
        username = row['Twitter']
        if pd.isna(username):
            continue

        url = f"https://x.com/{username}"
        driver.get(url)
        time.sleep(random.randint(5, 8))

        try:
            posts_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "posts")]'))
            )
            num_posts = posts_element.text
            num_posts = re.sub(r'\s*posts', '', num_posts)
            num_posts = convert_to_number(num_posts)
        except Exception:
            num_posts = "N/A"

        try:
            followers_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/verified_followers")]//span'))
            )
            num_followers = followers_element.text
            num_followers = convert_to_number(num_followers)
        except Exception:
            num_followers = "N/A"

        try:
            join_date_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Se unió")]'))
            )
            join_date = join_date_element.text.split()[-1]
        except Exception:
            join_date = "N/A"

        try:
            description_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="UserDescription"]'))
            )
            description = description_element.text
            description = re.sub(r'\s+', ' ', description).strip()
            description = re.sub(r'\s+\.', '.', description)
        except Exception:
            description = "N/A"

        if num_posts != convert_to_number(df.at[index, 'Posts']):
            df.at[index, 'Posts'] = num_posts
            cambios_realizados = True

        if num_followers != convert_to_number(df.at[index, 'Seguidores']):
            df.at[index, 'Seguidores'] = num_followers
            cambios_realizados = True

        if join_date != str(df.at[index, 'Comienzo en X/Twitter']):
            df.at[index, 'Comienzo en X/Twitter'] = join_date
            cambios_realizados = True

        if description != str(df.at[index, 'Descripción']):
            df.at[index, 'Descripción'] = description
            cambios_realizados = True

        print(f"Procesando datos de @{username}")
        print("----------------------")

    if cambios_realizados:
        all_sheets[sheet_name] = df

        with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
            for hoja, datos in all_sheets.items():
                datos.to_excel(writer, sheet_name=hoja, index=False)
        print(f"📄 Datos actualizados en: {file_path}")
    else:
        print("✅ No se realizaron cambios, todos los datos ya estaban actualizados.")

finally:
    driver.quit()
