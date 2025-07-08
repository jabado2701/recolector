import pandas as pd
import numpy as np
import multiprocessing
from typing import List, Dict

from extractor.FuncionesConjuntas import leer_cookies, setup_chromedriver
from extractor.comentarios.ApoyoComentarios import fusionar_archivos_comments, actualizar_conteo_comentarios
from extractor.comentarios.ExtractorComentarios import extraer_comentarios


class ControllerComentarios:
    def __init__(self, file_path: str, cantidad_comentarios: int = 5, num_procesos: int = 4):
        self.file_path = file_path
        self.cantidad_comentarios = cantidad_comentarios
        self.num_procesos = num_procesos
        self.driver_path = setup_chromedriver()
        self.cookies_list = leer_cookies()

    def preparar_enlaces_por_proceso(self) -> List[List[Dict]]:
        df_posts = pd.read_excel(self.file_path, sheet_name="Posts")
        df_metadata = pd.read_excel(self.file_path, sheet_name="Metadata")

        df_metadata["ID_Político"] = df_metadata["ID_Político"].ffill().astype(int)
        politicos_map = df_metadata.set_index("ID_Político")["Twitter"].to_dict()

        enlaces_info = []
        for _, row in df_posts.iterrows():
            enlace_post = row.get("Enlace_Post")
            id_politico = row.get("ID_Político")
            autor_twitter = politicos_map.get(id_politico, "")
            if pd.notna(enlace_post) and autor_twitter:
                enlaces_info.append({
                    "Enlace_Post": enlace_post,
                    "Autor_Twitter": autor_twitter
                })

        divididos = np.array_split(enlaces_info, self.num_procesos)
        return [list(grupo) for grupo in divididos]

    def ejecutar_extraccion_comentarios(self):
        if not self.cookies_list:
            print("⚠️ No hay cookies disponibles.")
            return

        enlaces_divididos = self.preparar_enlaces_por_proceso()

        print(f"🔄 Iniciando {self.num_procesos} procesos de comentarios...")
        procesos = []

        for i, grupo in enumerate(enlaces_divididos):
            print(f"🚀 Proceso {i}: {len(grupo)} posts.")
            p = multiprocessing.Process(
                target=extraer_comentarios,
                args=(grupo, self.file_path, i, self.cookies_list[i], self.driver_path, self.cantidad_comentarios)
            )
            procesos.append(p)
            p.start()

        for p in procesos:
            p.join()

        print("🔄 Fusionando archivos de comentarios...")
        fusionar_archivos_comments(self.file_path)

        print("🧮 Actualizando Comentarios_Extraidos en hoja 'Comentarios'...")
        actualizar_conteo_comentarios(self.file_path)
