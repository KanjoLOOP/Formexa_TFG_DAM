import sys
import os

def get_asset_path(relative_path):
    """
    Obtiene la ruta absoluta de un recurso (asset), funcionando tanto
    en desarrollo como en el ejecutable congelado con PyInstaller.
    
    Args:
        relative_path (str): Ruta relativa desde la raíz del proyecto (ej: 'assets/logo.png')
                             o desde la carpeta raíz si empieza con assets
    """
    if getattr(sys, 'frozen', False):
        # Estamos en el ejecutable
        base_path = sys._MEIPASS
    else:
        # Estamos en desarrollo
        # .../src/utils/resource_path.py -> .../src/utils -> .../src -> .../ (Project Root)
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    return os.path.join(base_path, relative_path)
