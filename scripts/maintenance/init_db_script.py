import os
from src.database.db_manager import DBManager

def init():
    # Ruta absoluta al schema.sql
    base_path = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(base_path, 'src', 'database', 'schema.sql')
    
    print(f"Buscando esquema en: {schema_path}")
    
    db = DBManager()
    if db.init_db(schema_path):
        print("Inicialización completada con éxito.")
    else:
        print("Falló la inicialización.")

if __name__ == "__main__":
    init()
