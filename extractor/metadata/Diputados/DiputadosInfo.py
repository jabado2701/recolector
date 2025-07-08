import os
import json
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup


def extraer_fecha_nacimiento(texto):
    match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
    return match.group(1) if match else None


def obtener_info_diputados():
    os.makedirs("Resultados", exist_ok=True)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    base_url = "https://www.congreso.es/es/busqueda-de-diputados"
    params_template = {
        "p_p_id": "diputadomodule",
        "p_p_lifecycle": "0",
        "p_p_state": "normal",
        "p_p_mode": "view",
        "_diputadomodule_mostrarFicha": "true",
        "idLegislatura": "XV",
        "mostrarAgenda": "false",
        "codParlamentario": None
    }
    headers = {"User-Agent": "Mozilla/5.0"}

    code = 1
    diputados_info = []

    while True:
        params_template["codParlamentario"] = str(code)
        response = requests.get(base_url, headers=headers, params=params_template)

        if "Se ha producido un error al obtener la información solicitada" in response.text:
            print(f"🚫 Fin alcanzado en codParlamentario={code}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("title")
        if not title_tag or "- " not in title_tag.text:
            print(f"⚠️ Sin nombre válido para codParlamentario={code}")
            break

        nombre = title_tag.text.split("- ")[0].strip()
        print(f"🔎 Procesando: {code}. {nombre}")

        url = f"{base_url}?p_p_id=diputadomodule&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_diputadomodule_mostrarFicha=true&codParlamentario={code}&idLegislatura=XV&mostrarAgenda=false"
        driver.get(url)

        info = {
            "codParlamentario": code,
            "nombre": nombre,
            "partido": None,
            "provincia": None,
            "legislaturas": [],
            "numero_legislaturas": 0,
            "edad": None
        }

        try:
            partido = driver.find_element(By.CLASS_NAME, "siglas-partido").text.strip()
            info["partido"] = partido
            print(f"✅ Partido: {partido}")
        except:
            print(f"⚠️ Partido no encontrado para {nombre}")

        try:
            provincia = driver.find_element(By.CLASS_NAME, "cargo-dip").text.strip()
            provincia = provincia.replace("Diputado por ", "").replace("Diputada por ", "")
            info["provincia"] = provincia
            print(f"✅ Provincia: {provincia}")
        except:
            print(f"⚠️ Provincia no encontrada para {nombre}")

        try:
            legislaturas_element = driver.find_elements(By.XPATH,
                                                        "//select[@id='_diputadomodule_legislaturasDiputado']/option")
            legislaturas = [re.search(r"\((\d{4})", leg.text).group(1) for leg in legislaturas_element if
                            re.search(r"\((\d{4})", leg.text)]
            legislaturas.sort()
            info["legislaturas"] = legislaturas
            info["numero_legislaturas"] = len(legislaturas)
            print(f"📜 Legislaturas: {', '.join(legislaturas)}")
        except:
            print(f"⚠️ Legislaturas no encontradas para {nombre}")

        try:
            nacimiento_element = driver.find_element(By.XPATH,
                                                     "//p[contains(text(), 'Nacido el') or contains(text(), 'Nacida el')]")
            fecha_str = extraer_fecha_nacimiento(nacimiento_element.text)
            if fecha_str:
                fecha_nacimiento = datetime.strptime(fecha_str, "%d/%m/%Y")
                edad = datetime.now().year - fecha_nacimiento.year
                info["edad"] = edad
                print(f"🎂 Edad: {edad}")
        except:
            print(f"⚠️ Fecha de nacimiento no encontrada para {nombre}")

        diputados_info.append(info)
        code += 1

    driver.quit()
    print("🚪 Navegador cerrado.")

    with open("Insertar ruta al archivo JSON con datos de diputados", "w", encoding="utf-8") as f_json:
        json.dump(diputados_info, f_json, ensure_ascii=False, indent=2)

    print("✅ Archivo guardado correctamente en 'Insertar ruta al archivo JSON con datos de diputados'")


if __name__ == "__main__":
    obtener_info_diputados()
