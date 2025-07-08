import pandas as pd
from deep_translator import GoogleTranslator


class TraductorPoliticos:
    IDIOMA_CODIGOS = {
        'español': 'es',
        'inglés': 'en',
        'catalán': 'ca',
        'gallego': 'gl',
        'vasco': 'eu',
        'francés': 'fr',
        'portugués': 'pt',
        'italiano': 'it',
        'alemán': 'de',
        'latín': 'la',
        'asturiano': 'es',  # no soportado por el traductor
        'hebreo': 'iw',
        'romaní': 'es'  # no soportado por el traductor
    }

    def __init__(self, ruta_excel: str):
        self.ruta_excel = ruta_excel

    def traducir_texto(self, texto: str, idioma_legible: str, fila: int, total: int, hoja: str) -> str:
        codigo = self.IDIOMA_CODIGOS.get(idioma_legible.lower(), 'auto')

        try:
            if codigo == 'es':
                return texto

            print(f"🔄 Traduciendo del {idioma_legible} en la fila {fila + 1}/{total} de '{hoja}'")
            return GoogleTranslator(source=codigo, target="es").translate(texto)

        except Exception as e:
            print(f"⚠️ Error al traducir: {texto[:30]}... ({idioma_legible}) — {e}")
            return texto

    def traducir_posts(self) -> None:
        print("🔁 Traduciendo hoja 'Posts'...")
        try:
            df = pd.read_excel(self.ruta_excel, sheet_name="Posts")
        except Exception as e:
            print(f"❌ No se pudo abrir la hoja 'Posts': {e}")
            return

        if not {"Contenido", "Idioma"}.issubset(df.columns):
            print("❌ La hoja 'Posts' no contiene las columnas requeridas.")
            return

        total = len(df)
        df["Contenido_Traducido"] = [
            self.traducir_texto(row["Contenido"], row["Idioma"], idx, total, "Posts")
            if row["Idioma"].lower() != "español" else row["Contenido"]
            for idx, row in df.iterrows()
        ]

        self._guardar_hoja(df, "Posts")
        print("✅ Traducciones completadas en hoja 'Posts'.")

    def traducir_comentarios(self) -> None:
        print("🔁 Traduciendo hoja 'Comentarios'...")
        try:
            df = pd.read_excel(self.ruta_excel, sheet_name="Comentarios")
        except Exception as e:
            print(f"❌ No se pudo abrir la hoja 'Comentarios': {e}")
            return

        columnas_necesarias = {"Contenido", "Respuesta", "Idioma_Comentario", "Idioma_Respuesta"}
        if not columnas_necesarias.issubset(df.columns):
            print("❌ La hoja 'Comentarios' no contiene las columnas requeridas.")
            return

        total = len(df)
        df["Comentario_Traducido"] = [
            self.traducir_texto(row["Contenido"], row["Idioma_Comentario"], idx, total, "Comentarios")
            if row["Idioma_Comentario"].lower() != "español" else row["Contenido"]
            for idx, row in df.iterrows()
        ]

        df["Respuesta_Traducida"] = [
            self.traducir_texto(row["Respuesta"], row["Idioma_Respuesta"], idx, total, "Comentarios")
            if row["Idioma_Respuesta"].lower() not in {"español", "no"} else row["Respuesta"]
            for idx, row in df.iterrows()
        ]

        self._guardar_hoja(df, "Comentarios")
        print("✅ Traducciones completadas en hoja 'Comentarios'.")

    def _guardar_hoja(self, df: pd.DataFrame, hoja: str) -> None:
        try:
            with pd.ExcelWriter(self.ruta_excel, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                df.to_excel(writer, sheet_name=hoja, index=False)
        except Exception as e:
            print(f"⚠️ Error al guardar la hoja '{hoja}': {e}")

    def ejecutar(self) -> None:
        print(f"📂 Procesando archivo: {self.ruta_excel}")
        self.traducir_posts()
        self.traducir_comentarios()
        print("🏁 Proceso completado.")


if __name__ == "__main__":
    ruta = "Ruta al archivo Excel"
    traductor = TraductorPoliticos(ruta)
    traductor.ejecutar()
