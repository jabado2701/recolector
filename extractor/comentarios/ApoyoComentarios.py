import os
import re
import pandas as pd
from selenium.webdriver.common.by import By

COLUMNAS_COMENTARIOS = [
    "Enlace_Post", "Enlace_Comentario", "Contenido", "Fecha_Publicación",
    "Comentarios", "Retweets", "Likes", "Respuesta"
]


def fusionar_archivos_comments(file_path: str) -> None:
    """
    Fusiona archivos temporales de comentarios en el archivo principal.
    """
    archivos_temporales = [
        f for f in os.listdir()
        if f.startswith("comentarios_") and f.endswith(".xlsx")
    ]

    if os.path.exists(file_path):
        try:
            df_principal = pd.read_excel(file_path, sheet_name="Comentarios")
        except Exception:
            df_principal = pd.DataFrame(columns=COLUMNAS_COMENTARIOS)
    else:
        df_principal = pd.DataFrame(columns=COLUMNAS_COMENTARIOS)

    for temp_file in archivos_temporales:
        try:
            df_temp = pd.read_excel(temp_file, sheet_name="Comentarios")

            if set(COLUMNAS_COMENTARIOS).issubset(df_temp.columns):
                df_temp = df_temp[COLUMNAS_COMENTARIOS]
            else:
                print(f"⚠️ Columnas inesperadas en {temp_file}, se ajustarán.")
                df_temp = df_temp.reindex(columns=COLUMNAS_COMENTARIOS, fill_value="")

            df_principal = pd.concat([df_principal, df_temp], ignore_index=True)
            os.remove(temp_file)

        except Exception as e:
            print(f"⚠️ Error al procesar {temp_file}: {e}")

    with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df_principal.to_excel(writer, sheet_name="Comentarios", index=False)

    print(f"✅ Comentarios fusionados correctamente en: {file_path}")


def actualizar_conteo_comentarios(file_path: str) -> None:
    """
    Actualiza el conteo de comentarios por post en la hoja 'Posts'.
    """
    try:
        xls = pd.read_excel(file_path, sheet_name=None)

        df_comentarios = xls.get("Comentarios")
        if df_comentarios is None:
            print("⚠️ Hoja 'Comentarios' no encontrada.")
            return

        df_posts = xls.get("Posts")
        if df_posts is None:
            print("⚠️ Hoja 'Posts' no encontrada.")
            return

        conteo = df_comentarios["Enlace_Post"].value_counts().to_dict()
        df_posts["Comentarios_Extraidos"] = df_posts["Enlace_Post"].map(conteo).fillna(0).astype(int)

        xls["Posts"] = df_posts
        with pd.ExcelWriter(file_path, engine="openpyxl", mode="w") as writer:
            for nombre_hoja, df in xls.items():
                df.to_excel(writer, sheet_name=nombre_hoja, index=False)

        print("✅ Conteo de comentarios actualizado en hoja 'Posts'.")

    except Exception as e:
        print(f"⚠️ Error al actualizar el conteo de comentarios: {e}")


def es_descubre_mas(block) -> bool:
    """
    Detecta si el bloque actual corresponde a la sección 'Descubre más / Discover more'.
    """
    try:
        spans = block.find_elements(By.XPATH, './/span')
        for span in spans:
            texto = span.text.strip().lower()
            if texto:
                print(f"🔍 Texto detectado en span: '{texto}'")
            if "descubre más" in texto or "discover more" in texto:
                print("⛔ Sección 'Descubre más' encontrada.")
                return True
    except Exception as e:
        print(f"⚠️ Error al analizar bloque: {e}")
    return False

