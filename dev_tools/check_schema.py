import sqlite3

def check_filaments_schema():
    conn = sqlite3.connect('../data/gestor3d.db')
    cursor = conn.cursor()
    
    try:
        # Ver esquema completo de filaments
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='filaments'")
        schema = cursor.fetchone()
        
        print("=== FILAMENTS TABLE SCHEMA ===")
        if schema:
            print(schema[0])
            
            # Verificar si hay referencias a users_old
            if 'users_old' in schema[0].lower():
                print("\n⚠️  FOUND REFERENCE TO users_old IN SCHEMA!")
                print("This table needs to be recreated without the reference.")
        else:
            print("Table 'filaments' not found!")
            
        # Ver foreign keys
        cursor.execute("PRAGMA foreign_key_list(filaments)")
        fks = cursor.fetchall()
        print(f"\n=== FOREIGN KEYS ({len(fks)}) ===")
        for fk in fks:
            print(fk)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    check_filaments_schema()
