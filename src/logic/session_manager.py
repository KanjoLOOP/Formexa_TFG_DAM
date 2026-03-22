import json
import os
import hashlib
from src.utils.logger import logger

class SessionManager:
    """Gestor de sesión para recordar credenciales."""
    
    # .../src/logic/session_manager.py -> .../src/logic -> .../src -> .../ (Project Root)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    SESSION_FILE = os.path.join(BASE_DIR, "data", "session.json")
    
    @staticmethod
    def save_session(username, password):
        """Guarda el usuario y un token derivado de la contraseña (no la contraseña en claro).
        
        El token se genera con SHA-256 sobre username + password + salt fijo.
        De esta forma nunca se almacena la contraseña real en el archivo JSON.
        """
        # C4: Generamos un token simple — nunca guardamos la contraseña en texto plano
        token = hashlib.sha256((username + password + "formexa_salt").encode()).hexdigest()
        data = {
            "username": username,
            "token": token
        }
        try:
            with open(SessionManager.SESSION_FILE, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            logger.error(f"Error guardando sesión: {e}")
            return False
            
    @staticmethod
    def load_session():
        """Carga la sesión guardada.
        
        Returns:
            tuple: (username, token) o (None, None) si no hay sesión guardada.
        """
        if not os.path.exists(SessionManager.SESSION_FILE):
            return None, None
            
        try:
            with open(SessionManager.SESSION_FILE, 'r') as f:
                data = json.load(f)
                # C4: Devolvemos username y token, nunca la contraseña
                return data.get("username"), data.get("token")
        except Exception as e:
            logger.error(f"Error cargando sesión: {e}")
            return None, None
            
    @staticmethod
    def clear_session():
        """Borra el archivo de sesión."""
        if os.path.exists(SessionManager.SESSION_FILE):
            try:
                os.remove(SessionManager.SESSION_FILE)
                return True
            except Exception as e:
                logger.error(f"Error borrando sesión: {e}")
                return False
        return True
