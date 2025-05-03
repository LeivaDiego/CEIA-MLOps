# Modulo para la configuración de logging en el proyecto

# --- Librerias ---
import logging

def get_logger(name=__name__):
    """
    Crea y retorna un logger configurado.

    Args:
        name (str): Nombre del logger. Por defecto, el nombre del módulo.

    Returns:
        logging.Logger: Logger configurado.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s | %(name)s | %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
