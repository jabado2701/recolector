import pandas as pd


class AnalizadorComentarios:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df_posts = None
        self.distribucion = {}

    def cargar_datos(self):
        """Carga la hoja 'Posts' del archivo Excel."""
        try:
            self.df_posts = pd.read_excel(self.file_path, sheet_name="Posts")
            print("✅ Datos cargados correctamente.")
        except Exception as e:
            print(f"❌ Error al cargar datos: {e}")

    def analizar_comentarios(self):
        """Analiza la cantidad de posts por número de comentarios extraídos."""
        if self.df_posts is None:
            print("⚠️ No se han cargado los datos. Ejecuta 'cargar_datos()' primero.")
            return

        conteo = self.df_posts["Comentarios_Extraidos"].value_counts().sort_index()
        self.distribucion = conteo.to_dict()

    def mostrar_resultado(self):
        """Muestra los resultados en formato legible."""
        if not self.distribucion:
            print("⚠️ No hay datos para mostrar. Ejecuta 'analizar_comentarios()' primero.")
            return

        print("\n📊 Distribución de comentarios por post:\n")
        for comentarios, cantidad in self.distribucion.items():
            print(f"{comentarios} comentario(s): {cantidad} post(s)")


if __name__ == "__main__":
    file_path = "Ruta al archivo Excel"

    analizador = AnalizadorComentarios(file_path)
    analizador.cargar_datos()
    analizador.analizar_comentarios()
    analizador.mostrar_resultado()
