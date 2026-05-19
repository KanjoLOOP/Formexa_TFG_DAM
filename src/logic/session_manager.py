import json
import os
import secrets
from datetime import datetime, timedelta

from src.database.db_manager import DBManager
from src.utils.logger import logger


class SessionManager:

    @staticmethod
    def _get_session_file() -> str:
        app_data_dir = DBManager._get_user_data_dir()
        return os.path.join(app_data_dir, 'session.json')

    @staticmethod
    def save_session(user_id: int) -> bool:
        token = secrets.token_urlsafe(32)
        expires_at = (datetime.now() + timedelta(days=30)).isoformat()
        db = DBManager()
        try:
            db.execute_query(
                "INSERT INTO user_tokens (token, user_id, expires_at) VALUES (?, ?, ?)",
                (token, user_id, expires_at)
            )
            session_file = SessionManager._get_session_file()
            with open(session_file, 'w') as f:
                json.dump({"token": token}, f)
            return True
        except Exception as e:
            logger.error(f"Error guardando sesión: {e}")
            return False

    @staticmethod
    def load_session():
        """Returns user_id if a valid, unexpired token exists, else None."""
        session_file = SessionManager._get_session_file()
        if not os.path.exists(session_file):
            return None
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
            token = data.get("token")
            if not token:
                return None
            db = DBManager()
            result = db.fetch_one(
                "SELECT user_id, expires_at FROM user_tokens WHERE token = ?",
                (token,)
            )
            if not result:
                return None
            user_id, expires_at_str = result
            if datetime.fromisoformat(expires_at_str) < datetime.now():
                db.execute_query("DELETE FROM user_tokens WHERE token = ?", (token,))
                os.remove(session_file)
                return None
            return user_id
        except Exception as e:
            logger.error(f"Error cargando sesión: {e}")
            return None

    @staticmethod
    def clear_session() -> bool:
        session_file = SessionManager._get_session_file()
        try:
            if os.path.exists(session_file):
                try:
                    with open(session_file, 'r') as f:
                        data = json.load(f)
                    token = data.get("token")
                    if token:
                        DBManager().execute_query(
                            "DELETE FROM user_tokens WHERE token = ?", (token,)
                        )
                except Exception:
                    pass
                os.remove(session_file)
            return True
        except Exception as e:
            logger.error(f"Error borrando sesión: {e}")
            return False
