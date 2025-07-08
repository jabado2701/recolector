import multiprocessing
from extractor.FuncionesConjuntas import setup_chromedriver
from extractor.posts.ControllerPosts import PostsController


def run():
    print(f"🌀 Ejecutando main() en proceso PID {multiprocessing.current_process().pid}")
    file_path = "Insertar ruta al archivo Excel"
    driver_path = setup_chromedriver()

    # Configuración
    config = {
        "modo_individual": False,
        "por_fecha": False,
        "cantidad_tweets": 1,
        "fecha_inicio": "2025-06-09",
        "fecha_fin": "2025-06-10",
        "username": "sanchezcastejon"
    }

    controller = PostsController(file_path, driver_path)

    if config["modo_individual"]:
        if config["por_fecha"]:
            controller.ejecutar_individual(
                config["username"],
                fecha_inicio=config["fecha_inicio"],
                fecha_fin=config["fecha_fin"]
            )
        else:
            controller.ejecutar_individual(
                config["username"],
                cantidad=config["cantidad_tweets"]
            )
    else:
        if config["por_fecha"]:
            controller.ejecutar_grupal(
                fecha_inicio=config["fecha_inicio"],
                fecha_fin=config["fecha_fin"]
            )
        else:
            controller.ejecutar_grupal(
                cantidad=config["cantidad_tweets"]
            )


if __name__ == "__main__":
    multiprocessing.freeze_support()
    run()
