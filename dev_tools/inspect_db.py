import sqlite3

def inspect_database():
    try:
        conn = sqlite3.connect('../data/gestor3d.db')
        cursor = conn.cursor()
        
        # Ver todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        
        # Ver esquema de filaments
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='filaments'")
        schema = cursor.fetchone()
        print(f"\nFilaments schema:\n{schema[0] if schema else 'NOT FOUND'}")
        
        # Ver todos los triggers (incluyendo los de filaments)
        cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='trigger'")
        triggers = cursor.fetchall()
        print(f"\n\nAll triggers ({len(triggers)}):")
        for name, table, sql in triggers:
            print(f"\n--- Trigger: {name} on {table} ---")
            print(sql)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_database()
