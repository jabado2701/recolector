import pandas as pd
import os
import json


file_path = "Insertar ruta al archivo Excel"
json_path = "Insertar ruta al archivo JSON con datos de diputados"

provincias_por_ccaa = {
    "Andalucía": ["Almería", "Cádiz", "Córdoba", "Granada", "Huelva", "Jaén", "Málaga", "Sevilla"],
    "Aragón": ["Huesca", "Teruel", "Zaragoza"],
    "Principado de Asturias": ["Asturias"],
    "Islas Baleares": ["Balears (Illes)"],
    "Canarias": ["Palmas (Las)", "S/C Tenerife"],
    "Cantabria": ["Cantabria"],
    "Castilla-La Mancha": ["Albacete", "Ciudad Real", "Cuenca", "Guadalajara", "Toledo"],
    "Castilla y León": ["Ávila", "Burgos", "León", "Palencia", "Salamanca", "Segovia", "Soria", "Valladolid", "Zamora"],
    "Cataluña": ["Barcelona", "Girona", "Lleida", "Tarragona"],
    "Extremadura": ["Badajoz", "Cáceres"],
    "Galicia": ["Coruña (A)", "Lugo", "Ourense", "Pontevedra"],
    "Comunidad de Madrid": ["Madrid"],
    "Región de Murcia": ["Murcia"],
    "Comunidad Foral de Navarra": ["Navarra"],
    "País Vasco": ["Araba/Álava", "Bizkaia", "Gipuzkoa"],
    "La Rioja": ["Rioja (La)"],
    "Comunidad Valenciana": ["Alicante/Alacant", "Castellón/Castelló", "Valencia/València"]
}

partidos_por_base = {
    "PSOE": ["PSOE", "PSE-EE (PSOE)", "PSC-PSOE", "PSN-PSOE", "PSIB-PSOE", "PsdeG-PSOE"],
    "PP": ["PP"],
    "VOX": ["VOX"],
    "SUMAR": ["SUMAR"],
    "ERC": ["ERC"],
    "JxCAT-JUNTS": ["JxCAT-JUNTS"],
    "EH Bildu": ["EH Bildu"],
    "EAJ-PNV": ["EAJ-PNV"],
    "BNG": ["BNG"],
    "CCa": ["CCa"],
    "UPN": ["UPN"]
}


def obtener_comunidad(provincia):
    for comunidad, provincias in provincias_por_ccaa.items():
        if provincia in provincias:
            return comunidad
    return "No disponible"


def obtener_partido_base(partido):
    for base, partidos in partidos_por_base.items():
        if partido in partidos:
            return base
    return "No disponible"


def extraer_info_diputados(desde_excel):
    with open(json_path, "r", encoding="utf-8") as file:
        diputados_data = json.load(file)

    nombres_diputados = desde_excel.loc[desde_excel["Cargo"] == "Diputado", "Nombre"].dropna().tolist()

    resultados = []
    for nombre in nombres_diputados:
        print(f"🔄 Procesando diputado: {nombre}")
        match = next((d for d in diputados_data if nombre.lower() in d["nombre"].lower()), None)
        if match:
            provincia = match.get("provincia", "No disponible")
            comunidad = obtener_comunidad(provincia)
            partido = match.get("partido", "No disponible")
            partido_base = obtener_partido_base(partido)
            legislaturas = match.get("legislaturas", [])
            edad = match.get("edad", "No disponible")

            resultados.append([
                match["nombre"],
                comunidad,
                partido_base,
                ", ".join(legislaturas),
                len(legislaturas),
                edad
            ])
        else:
            print(f"⚠️ No se encontró información para: {nombre}")

    return pd.DataFrame(resultados,
                        columns=["Nombre", "Comunidad Autónoma", "Partido", "Legislaturas", "Número de Legislaturas", "Edad"])


def actualizar_excel():
    if os.path.exists(file_path):
        all_sheets = pd.read_excel(file_path, sheet_name=None)
    else:
        print(f"⚠️ No se encontró el archivo {file_path}.")
        return

    hoja_objetivo = "Metadata"
    if hoja_objetivo not in all_sheets:
        print(f"⚠️ No se encontró la hoja {hoja_objetivo}.")
        return

    df_excel = all_sheets[hoja_objetivo]
    df_diputados = extraer_info_diputados(df_excel)

    cambios_realizados = False

    for index, row in df_excel.iterrows():
        if str(row["Cargo"]).strip() != "Diputado":
            continue

        nombre_politico = str(row["Nombre"]).strip()
        match = df_diputados[df_diputados["Nombre"].str.contains(nombre_politico, na=False, case=False)]

        if not match.empty:
            match_data = match.iloc[0]

            for campo in ["Comunidad Autónoma", "Partido", "Legislaturas", "Número de Legislaturas", "Edad"]:
                if pd.isna(row[campo]) or row[campo] != match_data[campo]:
                    df_excel.at[index, campo] = match_data[campo]
                    cambios_realizados = True

    if cambios_realizados:
        all_sheets[hoja_objetivo] = df_excel
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
            for nombre_hoja, df_hoja in all_sheets.items():
                df_hoja.to_excel(writer, sheet_name=nombre_hoja, index=False)
        print(f"📄 Datos actualizados en {file_path}")
    else:
        print("✅ No se realizaron cambios, todos los datos ya estaban actualizados.")


if __name__ == "__main__":
    actualizar_excel()
