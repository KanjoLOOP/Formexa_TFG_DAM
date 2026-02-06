import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name="Gestor3D"):
    """
    Configura y devuelve una instancia de logger.
    Crea una carpeta 'logs' si no existe.
    """
    # 1. Crear directorio de logs
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, 'app.log')

    # 2. Configurar el logger base
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Evitar duplicar handlers si se llama varias veces
    if not logger.handlers:
        # 3. Formato
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 4. Handler de Consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 5. Handler de Archivo (Rotativo: 5MB, mantiene 3 backups)
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Instancia global para importar fácilmente
logger = setup_logger()
