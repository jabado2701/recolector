import multiprocessing
import pandas as pd
from ExtractorPosts import TweetExtractor
from extractor.FuncionesConjuntas import leer_cookies
from ApoyoPosts import dividir_cuentas_entre_procesos, fusionar_archivos


class PostsController:
    def __init__(self, file_path: str, driver_path: str):
        """
        Controlador de ejecución de extracción de tweets.
        """
        self.file_path = file_path
        self.driver_path = driver_path
        self.cookies = leer_cookies()

    def _leer_metadata(self) -> list[dict]:
        df = pd.read_excel(self.file_path, sheet_name="Metadata")
        df["ID_Político"] = df["ID_Político"].ffill().astype(int)
        return df[["ID_Político", "Twitter"]].dropna().to_dict(orient="records")

    def _run_grupal_worker_entre_fechas(self, politicos: list, process_id: int, fecha_inicio: str, fecha_fin: str):
        extractor = TweetExtractor(
            file_path=self.file_path,
            driver_path=self.driver_path,
            cookies=self.cookies[process_id],
            process_id=process_id,
            headless=True
        )
        extractor.extraer_para_grupo_entre_fechas(politicos, fecha_inicio, fecha_fin)

    def _run_grupal_worker(self, politicos: list, process_id: int, cantidad: int):
        extractor = TweetExtractor(
            file_path=self.file_path,
            driver_path=self.driver_path,
            cookies=self.cookies[process_id],
            process_id=process_id,
            headless=True,
            cantidad=cantidad
        )
        extractor.extraer_para_grupo(politicos)

    def _lanzar_procesos_grupales(self, grupos: list, cantidad: int = None,
                                  fecha_inicio: str = None, fecha_fin: str = None) -> list:
        procesos = []
        for i, grupo in enumerate(grupos):
            print(f"✅ Proceso {i} contiene {len(grupo)} elementos")
            if fecha_inicio and fecha_fin:
                p = multiprocessing.Process(
                    target=self._run_grupal_worker_entre_fechas,
                    args=(grupo, i, fecha_inicio, fecha_fin)
                )
            else:
                p = multiprocessing.Process(
                    target=self._run_grupal_worker,
                    args=(grupo, i, cantidad)
                )
            procesos.append(p)
            p.start()
        return procesos

    def ejecutar_grupal(self, cantidad: int = None, fecha_inicio: str = None, fecha_fin: str = None):
        """
        Ejecuta la extracción en modo grupal.
        """
        politicos = self._leer_metadata()

        if not self.cookies:
            print("⚠️ No hay cookies disponibles.")
            return

        num_procesos = min(4, len(self.cookies), len(politicos))
        if num_procesos == 0:
            print("⚠️ No hay suficientes cuentas o cookies.")
            return

        cuentas_divididas = dividir_cuentas_entre_procesos(politicos, num_procesos)
        procesos = self._lanzar_procesos_grupales(cuentas_divididas, cantidad, fecha_inicio, fecha_fin)

        for p in procesos:
            p.join()

        fusionar_archivos(self.file_path)

    def ejecutar_individual(self, username: str, cantidad: int = None,
                            fecha_inicio: str = None, fecha_fin: str = None):
        """
        Ejecuta la extracción de un solo usuario.
        """
        if not self.cookies:
            print("⚠️ No hay cookies disponibles.")
            return

        extractor = TweetExtractor(
            file_path=self.file_path,
            driver_path=self.driver_path,
            cookies=self.cookies[0],
            headless=False,
            cantidad=cantidad or 20
        )

        if fecha_inicio and fecha_fin:
            extractor.extraer_para_usuario_entre_fechas(username, fecha_inicio, fecha_fin)
        else:
            extractor.extraer_para_usuario(username)
