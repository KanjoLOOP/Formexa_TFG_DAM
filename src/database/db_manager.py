import sqlite3
import os
import sys
from src.utils.logger import logger
from sqlite3 import Error

class DBManager:
    def __init__(self, db_file='gestor3d.db'):
        # Determinar directorio base
        if getattr(sys, 'frozen', False):
            # Si corre como exe, usar el directorio del ejecutable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Si corre como script, subir 3 niveles desde este archivo
            # .../src/database/db_manager.py -> .../src/database -> .../src -> .../ (Project Root)
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
        # Asegurar que existe la carpeta data
        data_dir = os.path.join(base_dir, 'data')
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir)
            except OSError as e:
                logger.error(f"Error creando directorio data: {e}")

        if db_file == 'gestor3d.db':
            self.db_file = os.path.join(data_dir, db_file)
        else:
            self.db_file = db_file
            
        self.connection = None

    def connect(self):
        """Establece la conexión con la base de datos SQLite."""
        try:
            self.connection = sqlite3.connect(self.db_file)
            # Habilitar claves foráneas
            self.connection.execute("PRAGMA foreign_keys = 1")
            return True
        except Error as e:
            logger.error(f"Error al conectar a SQLite: {e}")
            return False

    def disconnect(self):
        """Cierra la conexión."""
        if self.connection:
            self.connection.close()
            # print("Conexión cerrada")

    def execute_query(self, query, params=()):
        """Ejecuta una consulta (INSERT, UPDATE, DELETE)."""
        if not self.connection:
            if not self.connect():
                raise Exception("No se pudo conectar a la base de datos")
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except Error as e:
            # Propagar la excepción para que el caller la maneje (ej: IntegrityError)
            raise e

    def fetch_query(self, query, params=()):
        """Ejecuta una consulta de selección (SELECT)."""
        if not self.connection:
            if not self.connect():
                return None

        # Configurar row_factory para obtener diccionarios
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            result = [dict(row) for row in cursor.fetchall()]
            return result
        except Error as e:
            print(f"Error al obtener datos: {e}")
            return None
        finally:
            cursor.close()
    
    def fetch_one(self, query, params=()):
        """Ejecuta una consulta de selección y retorna solo una fila."""
        if not self.connection:
            if not self.connect():
                return None

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error al obtener datos: {e}")
            return None
        finally:
            cursor.close()

    def init_db(self, schema_file):
        """Inicializa la base de datos ejecutando un script SQL."""
        try:
            if not self.connect():
                return False
                
            with open(schema_file, 'r') as f:
                sql_script = f.read()
            
            cursor = self.connection.cursor()
            cursor.executescript(sql_script)
            self.connection.commit()
            cursor.close()
            logger.info("Base de datos SQLite inicializada correctamente.")
            return True
        except Error as e:
            logger.error(f"Error al inicializar la base de datos: {e}")
            return False
        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {schema_file}")
            return False

