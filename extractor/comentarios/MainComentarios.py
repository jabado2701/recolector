import multiprocessing
from extractor.comentarios.ControllerComentarios import ControllerComentarios


def main():
    ruta_excel = "Ruta al archivo Excel"
    cantidad_objetivo = 1  # Comentarios por post
    num_procesos = 4  # Ajustable
    procesos_a_usar = min(num_procesos, multiprocessing.cpu_count() - 1)

    controlador = ControllerComentarios(
        file_path=ruta_excel,
        cantidad_comentarios=cantidad_objetivo,
        num_procesos=procesos_a_usar
    )
    controlador.ejecutar_extraccion_comentarios()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
