import sqlite3

def clean_triggers():
    db_path = '../data/gestor3d.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Listar triggers
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'trigger'")
        triggers = cursor.fetchall()
        
        print("Triggers encontrados:", triggers)
        
        for trigger in triggers:
            trigger_name = trigger[0]
            print(f"Eliminando trigger: {trigger_name}")
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
            
        conn.commit()
        print("Triggers eliminados correctamente.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clean_triggers()
