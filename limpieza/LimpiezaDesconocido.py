import pandas as pd
from openpyxl import load_workbook


def limpiar_y_corregir_idiomas(file_path):
    try:
        df_posts = pd.read_excel(file_path, sheet_name="Posts")
        df_comentarios = pd.read_excel(file_path, sheet_name="Comentarios")

        print("🔍 Cargando hojas y buscando registros con idioma 'desconocido'...")

        posts_desconocidos = df_posts[df_posts["Idioma"] == "desconocido"]
        enlaces_a_eliminar = posts_desconocidos["Enlace_Post"].tolist()
        print(f"🗑️ Posts eliminados: {len(posts_desconocidos)}")
        df_posts_filtrado = df_posts[df_posts["Idioma"] != "desconocido"].copy()

        comentarios_ligados = df_comentarios[df_comentarios["Enlace_Post"].isin(enlaces_a_eliminar)]
        print(f"🗑️ Comentarios eliminados por pertenecer a posts desconocidos: {len(comentarios_ligados)}")
        df_comentarios = df_comentarios[~df_comentarios["Enlace_Post"].isin(enlaces_a_eliminar)].copy()

        comentarios_desconocido = df_comentarios[df_comentarios["Idioma_Comentario"] == "desconocido"]
        print(f"🗑️ Comentarios eliminados por idioma desconocido: {len(comentarios_desconocido)}")
        df_comentarios = df_comentarios[df_comentarios["Idioma_Comentario"] != "desconocido"].copy()

        respuestas_corregidas = df_comentarios["Idioma_Respuesta"] == "desconocido"
        count_respuestas = respuestas_corregidas.sum()
        df_comentarios.loc[respuestas_corregidas, "Idioma_Respuesta"] = "No"
        df_comentarios.loc[respuestas_corregidas, "Respuesta"] = "No"
        print(f"🩹 Respuestas corregidas con 'No': {count_respuestas}")

        df_posts_filtrado = df_posts_filtrado.dropna(how='all').reset_index(drop=True)
        df_comentarios = df_comentarios.dropna(how='all').reset_index(drop=True)

        with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df_posts_filtrado.to_excel(writer, sheet_name="Posts", index=False)
            df_comentarios.to_excel(writer, sheet_name="Comentarios", index=False)

        print("✅ Archivo limpiado y actualizado correctamente.")

    except Exception as e:
        print(f"⚠️ Error durante la limpieza: {e}")


if __name__ == "__main__":
    ruta_excel = "Ruta al archivo Excel"
    limpiar_y_corregir_idiomas(ruta_excel)
