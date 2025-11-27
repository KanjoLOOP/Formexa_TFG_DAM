import hashlib
import sqlite3
from datetime import datetime
from src.database.db_manager import DBManager

class AuthManager:
    """Gestor de autenticación de usuarios."""
    
    def __init__(self):
        self.db = DBManager()
        self.current_user = None
    
    def _hash_password(self, password):
        """Genera hash SHA-256 de la contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password, email=""):
        """Registra un nuevo usuario."""
        try:
            password_hash = self._hash_password(password)
            query = """
                INSERT INTO users (username, password_hash, email, is_guest)
                VALUES (?, ?, ?, 0)
            """
            self.db.execute_query(query, (username, password_hash, email))
            return True, "Usuario registrado exitosamente"
        except sqlite3.IntegrityError:
            return False, "El nombre de usuario ya existe"
        except Exception as e:
            return False, f"Error al registrar: {str(e)}"
    
    def login(self, username, password):
        """Inicia sesión con usuario y contraseña."""
        try:
            password_hash = self._hash_password(password)
            query = """
                SELECT id, username, is_guest, email
                FROM users
                WHERE username = ? AND password_hash = ? AND is_guest = 0
            """
            result = self.db.fetch_one(query, (username, password_hash))
            
            if result:
                self.current_user = {
                    'id': result[0],
                    'username': result[1],
                    'is_guest': result[2],
                    'email': result[3]
                }
                
                # Actualizar last_login
                update_query = "UPDATE users SET last_login = ? WHERE id = ?"
                self.db.execute_query(update_query, (datetime.now(), result[0]))
                
                return True, "Inicio de sesión exitoso"
            else:
                return False, "Usuario o contraseña incorrectos"
        except Exception as e:
            return False, f"Error al iniciar sesión: {str(e)}"
    
    def login_as_guest(self):
        """Inicia sesión como invitado (no persiste en BD)."""
        self.current_user = {
            'id': -1,
            'username': 'Invitado',
            'is_guest': 1,
            'email': ''
        }
        return True, "Sesión de invitado iniciada"
    
    def logout(self):
        """Cierra la sesión actual."""
        self.current_user = None
    
    def get_current_user(self):
        """Retorna el usuario actual o None."""
        return self.current_user
    
    def is_guest(self):
        """Verifica si el usuario actual es invitado."""
        return self.current_user and self.current_user.get('is_guest') == 1
    
    def is_logged_in(self):
        """Verifica si hay un usuario logueado."""
        return self.current_user is not None
