import hashlib
import re
import sqlite3
import time
from datetime import datetime

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from src.database.db_manager import DBManager


class AuthManager:

    def __init__(self):
        self.db = DBManager()
        self.current_user = None
        self._ph = PasswordHasher()
        self._failed_attempts = {}  # {username: [count, last_attempt_ts]}

    def _hash_password(self, password: str) -> str:
        return self._ph.hash(password)

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        if stored_hash.startswith('$argon2'):
            try:
                return self._ph.verify(stored_hash, password)
            except VerifyMismatchError:
                return False
        elif '$' in stored_hash:
            # salt$sha256 format
            try:
                salt, hash_value = stored_hash.split('$', 1)
                return hashlib.sha256((salt + password).encode()).hexdigest() == hash_value
            except ValueError:
                return False
        else:
            # legacy pure SHA-256
            return hashlib.sha256(password.encode()).hexdigest() == stored_hash

    def _is_rate_limited(self, username: str) -> bool:
        entry = self._failed_attempts.get(username)
        if not entry:
            return False
        count, last_ts = entry
        if count >= 5:
            if time.time() - last_ts < 60:
                return True
            del self._failed_attempts[username]
        return False

    def _record_failed_attempt(self, username: str):
        count = self._failed_attempts.get(username, [0, 0])[0]
        self._failed_attempts[username] = [count + 1, time.time()]

    def _reset_attempts(self, username: str):
        self._failed_attempts.pop(username, None)

    def register(self, username: str, password: str, email: str = "") -> tuple:
        if len(username) < 3 or not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Usuario inválido: mínimo 3 caracteres, solo letras, números, _ y -"
        if len(password) < 8:
            return False, "Contraseña demasiado corta: mínimo 8 caracteres"
        try:
            password_hash = self._hash_password(password)
            query = "INSERT INTO users (username, password_hash, email, is_guest) VALUES (?, ?, ?, 0)"
            self.db.execute_query(query, (username, password_hash, email))
            return True, "Usuario registrado exitosamente"
        except sqlite3.IntegrityError:
            return False, "El nombre de usuario ya existe"
        except Exception as e:
            return False, f"Error al registrar: {str(e)}"

    def login(self, username: str, password: str) -> tuple:
        if self._is_rate_limited(username):
            return False, "Demasiados intentos, espera un minuto"
        try:
            query = "SELECT id, username, password_hash, is_guest, email FROM users WHERE username = ? AND is_guest = 0"
            result = self.db.fetch_one(query, (username,))

            if result and self._verify_password(password, result[2]):
                self._reset_attempts(username)
                self.current_user = {
                    'id': result[0],
                    'username': result[1],
                    'is_guest': result[3],
                    'email': result[4],
                }
                self.db.execute_query(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now(), result[0])
                )
                # Rehash legacy hashes transparently
                if not result[2].startswith('$argon2'):
                    self.db.execute_query(
                        "UPDATE users SET password_hash = ? WHERE id = ?",
                        (self._hash_password(password), result[0])
                    )
                return True, "Inicio de sesión exitoso"
            else:
                self._record_failed_attempt(username)
                return False, "Usuario o contraseña incorrectos"
        except Exception as e:
            return False, f"Error al iniciar sesión: {str(e)}"

    def login_from_session(self, user_id: int) -> bool:
        """Auto-login from a validated session token (no password required)."""
        try:
            result = self.db.fetch_one(
                "SELECT id, username, is_guest, email FROM users WHERE id = ? AND is_guest = 0",
                (user_id,)
            )
            if result:
                self.current_user = {
                    'id': result[0],
                    'username': result[1],
                    'is_guest': result[2],
                    'email': result[3],
                }
                return True
            return False
        except Exception:
            return False

    def login_as_guest(self):
        self.current_user = {'id': -1, 'username': 'Invitado', 'is_guest': 1, 'email': ''}
        return True, "Sesión de invitado iniciada"

    def logout(self):
        self.current_user = None

    def get_current_user(self):
        return self.current_user

    def is_guest(self):
        return self.current_user and self.current_user.get('is_guest') == 1

    def is_logged_in(self):
        return self.current_user is not None
