import pandas as pd
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 0

LANG_MAP = {
    'es': 'español',
    'en': 'inglés',
    'gl': 'gallego',
    'eu': 'vasco',
    'ca': 'catalán',
    'fr': 'francés',
    'it': 'italiano',
    'de': 'alemán',
}


def detectar_idioma_texto(texto: str) -> str:
    try:
        lang = detect(texto)
        return LANG_MAP.get(lang, lang)
    except LangDetectException:
        return "desconocido"


def asignar_idiomas_a_posts(file_path: str) -> None:
    try:
        df = pd.read_excel(file_path, sheet_name="Posts")

        if "Contenido" not in df.columns:
            print("❌ No se encontró la columna 'Contenido' en la hoja 'Posts'.")
            return

        print("🔍 Detectando idiomas en publicaciones (Posts)...")
        df["Idioma"] = df["Contenido"].astype(str).apply(detectar_idioma_texto)

        with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df.to_excel(writer, sheet_name="Posts", index=False)

        print("✅ Idiomas asignados en hoja 'Posts'.")

    except Exception as e:
        print(f"⚠️ Error procesando hoja 'Posts': {e}")


def asignar_idiomas_a_comentarios(file_path: str) -> None:
    try:
        df = pd.read_excel(file_path, sheet_name="Comentarios")

        if not {"Contenido", "Respuesta"}.issubset(df.columns):
            print("❌ Faltan columnas necesarias ('Contenido' o 'Respuesta') en la hoja 'Comentarios'.")
            return

        print("🔍 Detectando idiomas en comentarios y respuestas...")
        df["Idioma_Comentario"] = df["Contenido"].astype(str).apply(detectar_idioma_texto)
        df["Idioma_Respuesta"] = df["Respuesta"].astype(str).apply(
            lambda x: "No" if x.strip().lower() == "no" else detectar_idioma_texto(x)
        )

        with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df.to_excel(writer, sheet_name="Comentarios", index=False)

        print("✅ Idiomas asignados en hoja 'Comentarios'.")

    except Exception as e:
        print(f"⚠️ Error procesando hoja 'Comentarios': {e}")


if __name__ == "__main__":
    RUTA_EXCEL = "Ruta al archivo Excel"
    asignar_idiomas_a_posts(RUTA_EXCEL)
    asignar_idiomas_a_comentarios(RUTA_EXCEL)
