import sqlite3
import os

def deep_clean_triggers():
    db_path = '../data/gestor3d.db'
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at {db_path}")
        return
    
    print(f"Database found at: {os.path.abspath(db_path)}")
    print(f"Database size: {os.path.getsize(db_path)} bytes")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Ver TODOS los objetos de la base de datos
        cursor.execute("SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY type, name")
        objects = cursor.fetchall()
        
        print(f"\n=== ALL DATABASE OBJECTS ({len(objects)}) ===")
        triggers_found = []
        
        for obj_type, name, table, sql in objects:
            if obj_type == 'trigger':
                triggers_found.append(name)
                print(f"\n[TRIGGER] {name} on table {table}")
                print(f"SQL: {sql}")
                
                # Verificar si menciona users_old
                if 'users_old' in (sql or '').lower():
                    print("  ⚠️  REFERENCES users_old - WILL BE DELETED")
        
        if not triggers_found:
            print("\n❌ NO TRIGGERS FOUND IN DATABASE")
            print("This is strange given the error. Checking for other issues...")
            
            # Verificar integridad
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()
            print(f"\nIntegrity check: {integrity}")
            
        else:
            print(f"\n\n=== DELETING {len(triggers_found)} TRIGGERS ===")
            for trigger_name in triggers_found:
                print(f"Dropping: {trigger_name}")
                cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
            
            conn.commit()
            print("\n✓ All triggers deleted successfully")
            
            # Verificar
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'")
            remaining = cursor.fetchone()[0]
            print(f"Remaining triggers: {remaining}")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    deep_clean_triggers()
