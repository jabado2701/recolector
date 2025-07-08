import pandas as pd
from openpyxl import load_workbook


class LimpiadorComentariosDuplicados:
    """Elimina comentarios duplicados en la hoja 'Comentarios'."""

    def __init__(self, file_path):
        self.file_path = file_path

    def eliminar(self):
        print("🔁 Iniciando verificación de comentarios duplicados...")

        try:
            df = pd.read_excel(self.file_path, sheet_name="Comentarios")

            if "Enlace_Comentario" not in df.columns:
                print("❌ [Comentarios] Columna 'Enlace_Comentario' no encontrada.")
                return

            duplicados = df[df.duplicated(subset="Enlace_Comentario", keep="first")]

            if duplicados.empty:
                print("✅ [Comentarios] No se encontraron comentarios duplicados.")
                return

            for _, fila in duplicados.iterrows():
                print(f"🗑️ [Comentarios] Eliminando duplicado: {fila['Enlace_Comentario']}")

            df_clean = df.drop_duplicates(subset="Enlace_Comentario", keep="first").reset_index(drop=True)

            with pd.ExcelWriter(self.file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                df_clean.to_excel(writer, sheet_name="Comentarios", index=False)

            print(f"✅ [Comentarios] Duplicados eliminados: {len(duplicados)}")
        except Exception as e:
            print(f"⚠️ [Comentarios] Error al procesar: {e}")


class VerificadorUnicidadEnlaces:
    """Elimina filas duplicadas de la hoja 'Posts' (sin dejar huecos)."""

    def __init__(self, file_path):
        self.file_path = file_path

    def verificar_y_eliminar(self):
        print("\n🔁 Iniciando verificación de enlaces duplicados en hoja 'Posts'...")

        if not self.file_path.endswith(".xlsx"):
            print("⚠️ [Posts] El archivo debe tener extensión .xlsx")
            return

        try:
            df = pd.read_excel(self.file_path, sheet_name="Posts")

            if "Enlace_Post" not in df.columns:
                print("❌ [Posts] Columna 'Enlace_Post' no encontrada.")
                return

            duplicados = df[df.duplicated(subset="Enlace_Post", keep="first")]

            if duplicados.empty:
                print("✅ [Posts] No se encontraron enlaces duplicados.")
                return

            for _, fila in duplicados.iterrows():
                print(f"🗑️ [Posts] Eliminando duplicado: {fila['Enlace_Post']}")

            df_clean = df.drop_duplicates(subset="Enlace_Post", keep="first").reset_index(drop=True)

            with pd.ExcelWriter(self.file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                df_clean.to_excel(writer, sheet_name="Posts", index=False)

            print(f"✅ [Posts] Filas eliminadas: {len(duplicados)}")

        except Exception as e:
            print(f"⚠️ [Posts] Error al procesar: {e}")


if __name__ == "__main__":
    ruta_excel = "Insertar ruta al archivo Excel"

    limpiador = LimpiadorComentariosDuplicados(ruta_excel)
    limpiador.eliminar()

    verificador = VerificadorUnicidadEnlaces(ruta_excel)
    verificador.verificar_y_eliminar()
