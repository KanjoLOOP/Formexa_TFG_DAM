import os
import json
import sys
from PyQt5.QtCore import QObject, pyqtSignal
from src.utils.logger import logger

class Translator(QObject):
    """Gestor de traducciones para soporte multi-idioma."""
    
    language_changed = pyqtSignal(str)  # Emite código de idioma cuando cambia
    
    _instance = None  # Singleton
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Translator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        super().__init__()
        self._initialized = True
        self._current_language = 'es'
        self._translations = {}
        self._load_language('es')
    
    def _get_locales_dir(self):
        """Obtiene el directorio de locales."""
        if getattr(sys, 'frozen', False):
            # En ejecutable frozen
            base_path = sys._MEIPASS
        else:
            # En desarrollo
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        return os.path.join(base_path, 'src', 'locales')
    
    def _load_language(self, lang_code):
        """Carga el archivo de traducciones para el idioma especificado."""
        locales_dir = self._get_locales_dir()
        lang_file = os.path.join(locales_dir, f'{lang_code}.json')
        
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self._translations = json.load(f)
            self._current_language = lang_code
            logger.info(f"Idioma cargado: {lang_code}")
            return True
        except FileNotFoundError:
            logger.error(f"Archivo de idioma no encontrado: {lang_file}")
            # Fallback a español si falla
            if lang_code != 'es':
                return self._load_language('es')
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar JSON de idioma {lang_code}: {e}")
            return False
    
    def set_language(self, lang_code):
        """Cambia el idioma actual y emite señal."""
        if lang_code == self._current_language:
            return  # Ya está en este idioma
        
        if self._load_language(lang_code):
            self.language_changed.emit(lang_code)
            self._save_language_preference(lang_code)
    
    def _save_language_preference(self, lang_code):
        """Guarda la preferencia de idioma."""
        try:
            # Usar el mismo sistema de AppData que la BD
            if sys.platform == 'win32':
                base = os.getenv('APPDATA') or os.path.expanduser('~')
                app_data_dir = os.path.join(base, 'Formexa3D')
            else:
                app_data_dir = os.path.expanduser('~/.local/share/Formexa3D')
            
            os.makedirs(app_data_dir, exist_ok=True)
            config_file = os.path.join(app_data_dir, 'config.json')
            
            # Leer configuración existente o crear nueva
            config = {}
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['language'] = lang_code
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error guardando preferencia de idioma: {e}")
    
    def load_saved_language(self):
        """Carga el idioma guardado en configuración."""
        try:
            if sys.platform == 'win32':
                base = os.getenv('APPDATA') or os.path.expanduser('~')
                app_data_dir = os.path.join(base, 'Formexa3D')
            else:
                app_data_dir = os.path.expanduser('~/.local/share/Formexa3D')
            
            config_file = os.path.join(app_data_dir, 'config.json')
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    lang_code = config.get('language', 'es')
                    if lang_code != self._current_language:
                        self.set_language(lang_code)
                        return lang_code
        except Exception as e:
            logger.error(f"Error cargando idioma guardado: {e}")
        
        return self._current_language
    
    def tr(self, key, **kwargs):
        """
        Obtiene una traducción por clave.
        
        Args:
            key: Clave de traducción (ej: "menu.home", "settings.title")
            **kwargs: Variables para reemplazar en el texto (ej: username="Juan")
        
        Returns:
            str: Texto traducido
        """
        keys = key.split('.')
        value = self._translations
        
        # Navegar por el diccionario anidado
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    logger.warning(f"Clave de traducción no encontrada: {key}")
                    return key  # Devolver la clave si no se encuentra
            else:
                logger.warning(f"Ruta de traducción inválida: {key}")
                return key
        
        # Si hay variables, reemplazarlas
        if kwargs and isinstance(value, str):
            try:
                value = value.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Variable no encontrada en traducción {key}: {e}")
        
        return value if isinstance(value, str) else key
    
    def get_current_language(self):
        """Retorna el código del idioma actual."""
        return self._current_language
    
    def get_language_name(self):
        """Retorna el nombre completo del idioma actual."""
        names = {
            'es': 'Español',
            'en': 'English',
            'fr': 'Français'
        }
        return names.get(self._current_language, 'Español')


# Instancia global del traductor
translator = Translator()
