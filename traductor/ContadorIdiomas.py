import pandas as pd


def contar_idiomas(file_path):
    print("📊 --- Conteo de idiomas en 'Posts' ---")
    try:
        df_posts = pd.read_excel(file_path, sheet_name="Posts")
        if "Idioma" in df_posts.columns:
            conteo_posts = df_posts["Idioma"].value_counts()
            for idioma, cantidad in conteo_posts.items():
                print(f"✅ {idioma}: {cantidad} posts")
        else:
            print("❌ La columna 'Idioma' no existe en la hoja 'Posts'.")
    except Exception as e:
        print(f"⚠️ Error al procesar 'Posts': {e}")

    print("\n📊 --- Conteo de idiomas en 'Comentarios' ---")
    try:
        df_com = pd.read_excel(file_path, sheet_name="Comentarios")

        if "Idioma_Comentario" in df_com.columns:
            print("🗨️ Idioma de comentarios:")
            conteo_com = df_com["Idioma_Comentario"].value_counts()
            for idioma, cantidad in conteo_com.items():
                print(f"   ✅ {idioma}: {cantidad} comentarios")

        if "Idioma_Respuesta" in df_com.columns:
            print("\n💬 Idioma de respuestas (excepto 'No'):")
            conteo_resp = df_com[df_com["Idioma_Respuesta"].str.lower() != "no"]["Idioma_Respuesta"].value_counts()
            for idioma, cantidad in conteo_resp.items():
                print(f"   ✅ {idioma}: {cantidad} respuestas")
    except Exception as e:
        print(f"⚠️ Error al procesar 'Comentarios': {e}")


if __name__ == "__main__":
    ruta_excel = "Ruta al archivo Excel"
    contar_idiomas(ruta_excel)
