import sqlite3
import os
import sys
from contextlib import contextmanager
from src.utils.logger import logger


class DBManager:
    _instance = None

    def __new__(cls, db_file='gestor3d.db'):
        if db_file != 'gestor3d.db':
            # Non-default path: new instance (for tests)
            instance = super().__new__(cls)
            instance._initialized = False
            return instance
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_file='gestor3d.db'):
        if getattr(self, '_initialized', False):
            return
        self._initialized = True
        self._in_transaction = False

        if db_file == 'gestor3d.db':
            app_data_dir = self._get_user_data_dir()
            data_dir = os.path.join(app_data_dir, 'data')
            try:
                os.makedirs(data_dir, exist_ok=True)
            except OSError as e:
                logger.error(f"Error creando directorio data: {e}")
                data_dir = app_data_dir
            self.db_file = os.path.join(data_dir, db_file)
        else:
            self.db_file = db_file

        self.connection = None
        logger.info(f"Base de datos configurada en: {self.db_file}")

    @staticmethod
    def _get_user_data_dir():
        if sys.platform == 'win32':
            base = os.getenv('APPDATA') or os.path.expanduser('~')
            app_data_dir = os.path.join(base, 'Formexa3D')
        else:
            app_data_dir = os.path.expanduser('~/.local/share/Formexa3D')
        try:
            os.makedirs(app_data_dir, exist_ok=True)
        except OSError as e:
            logger.error(f"Error creando directorio de usuario: {e}")
            app_data_dir = os.path.join(os.path.expanduser('~'), '.formexa3d')
            os.makedirs(app_data_dir, exist_ok=True)
        return app_data_dir

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_file)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.connection.execute("PRAGMA journal_mode = WAL")
            self.connection.execute("PRAGMA synchronous = NORMAL")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al conectar a SQLite: {e}")
            return False

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def _ensure_connected(self):
        if not self.connection:
            if not self.connect():
                raise Exception("No se pudo conectar a la base de datos")

    def query(self, sql, params=()) -> list:
        """SELECT múltiple → list[dict]"""
        self._ensure_connected()
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error en query: {e}")
            return []
        finally:
            cursor.close()

    def query_one(self, sql, params=()):
        """SELECT una fila → dict | None"""
        self._ensure_connected()
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error en query_one: {e}")
            return None
        finally:
            cursor.close()

    def execute(self, sql, params=()) -> int:
        """INSERT/UPDATE/DELETE → lastrowid or rowcount"""
        self._ensure_connected()
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params)
            if not self._in_transaction:
                self.connection.commit()
            return cursor.lastrowid or cursor.rowcount
        except sqlite3.Error as e:
            raise e
        finally:
            cursor.close()

    def executemany(self, sql, seq_of_params):
        self._ensure_connected()
        cursor = self.connection.cursor()
        try:
            cursor.executemany(sql, seq_of_params)
            if not self._in_transaction:
                self.connection.commit()
        except sqlite3.Error as e:
            raise e
        finally:
            cursor.close()

    @contextmanager
    def transaction(self):
        self._ensure_connected()
        self._in_transaction = True
        try:
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            self._in_transaction = False

    def init_db(self, schema_file):
        try:
            if not self.connect():
                return False
            with open(schema_file, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            cursor = self.connection.cursor()
            cursor.executescript(sql_script)
            self.connection.commit()
            cursor.close()
            logger.info("Base de datos SQLite inicializada correctamente.")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al inicializar la base de datos: {e}")
            return False
        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {schema_file}")
            return False
