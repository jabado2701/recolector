import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

url = "https://es.wikipedia.org/wiki/Anexo:Presidencias_auton%C3%B3micas_espa%C3%B1olas"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
response = requests.get(url, headers=headers)

file_path = "Insertar ruta al archivo Excel"

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", {"class": "wikitable"})
    rows = table.find_all("tr")[2:]

    presidentes_info = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 7:
            comunidad = cols[0].text.strip()
            presidente_completo = cols[3].text.strip()
            partido = cols[5].text.strip()

            presidente = presidente_completo.split("presidente")[0].split("presidenta")[0].strip()
            periodos = [a.text.strip() for a in cols[6].find_all("a")]
            periodos_str = ", ".join(periodos)
            num_periodos = len(periodos)

            link_politico = cols[3].find("a")
            wiki_link = f"https://es.wikipedia.org{link_politico['href']}" if link_politico else ""

            presidentes_info.append([presidente, comunidad, partido, periodos_str, num_periodos, wiki_link])

    df_wiki = pd.DataFrame(
        presidentes_info,
        columns=["Presidente", "Comunidad Autónoma", "Partido", "Legislaturas", "Número de Legislaturas", "Wiki_Link"]
    )

    if os.path.exists(file_path):
        all_sheets = pd.read_excel(file_path, sheet_name=None)
    else:
        print("⚠️ No se encontró el archivo Excel. Verifica la ruta.")
        exit()

    hoja_objetivo = "Metadata"
    if hoja_objetivo not in all_sheets:
        print(f"⚠️ No se encontró la hoja {hoja_objetivo}.")
        exit()

    df_excel = all_sheets[hoja_objetivo]

    for col in ["Comunidad Autónoma", "Partido", "Legislaturas", "Número de Legislaturas", "Edad"]:
        if col not in df_excel.columns:
            df_excel[col] = ""


    def obtener_edad(url):
        if not url:
            return None
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                nacimiento_label = soup.find(string=re.compile(r"Nacimiento"))
                if nacimiento_label:
                    parent = nacimiento_label.find_parent("tr")
                    if parent:
                        fecha_texto = parent.find("td").text.strip()
                        edad_match = re.search(r"\((\d+)\s*años\)", fecha_texto)
                        if edad_match:
                            return int(edad_match.group(1))
        except Exception as e:
            print(f"Error al obtener la edad desde {url}: {e}")
        return None


    cambios_realizados = False

    for index, row in df_excel.iterrows():
        nombre_politico = str(row["Nombre"]).strip()
        match = df_wiki[df_wiki["Presidente"].str.contains(nombre_politico, na=False, case=False)]

        if not match.empty:
            match_data = match.iloc[0]

            if pd.isna(row["Comunidad Autónoma"]) or row["Comunidad Autónoma"] != match_data["Comunidad Autónoma"]:
                df_excel.at[index, "Comunidad Autónoma"] = match_data["Comunidad Autónoma"]
                cambios_realizados = True

            if pd.isna(row["Partido"]) or row["Partido"] != match_data["Partido"]:
                df_excel.at[index, "Partido"] = match_data["Partido"]
                cambios_realizados = True

            if pd.isna(row["Legislaturas"]) or row["Legislaturas"] != match_data["Legislaturas"]:
                df_excel.at[index, "Legislaturas"] = match_data["Legislaturas"]
                cambios_realizados = True

            if pd.isna(row["Número de Legislaturas"]) or row["Número de Legislaturas"] != match_data[
                "Número de Legislaturas"]:
                df_excel.at[index, "Número de Legislaturas"] = match_data["Número de Legislaturas"]
                cambios_realizados = True

            edad_wiki = obtener_edad(match_data["Wiki_Link"])
            edad_actual = row["Edad"]

            if edad_wiki is not None and (pd.isna(edad_actual) or edad_actual != edad_wiki):
                df_excel.at[index, "Edad"] = edad_wiki
                cambios_realizados = True

    if cambios_realizados:
        all_sheets[hoja_objetivo] = df_excel

        with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
            for nombre_hoja, datos in all_sheets.items():
                datos.to_excel(writer, sheet_name=nombre_hoja, index=False)
        print(f"📄 Datos actualizados en: {file_path}")
    else:
        print("✅ No se realizaron cambios, todos los datos ya estaban actualizados.")

else:
    print(f"❌ Error al acceder a la página. Código de estado: {response.status_code}")
