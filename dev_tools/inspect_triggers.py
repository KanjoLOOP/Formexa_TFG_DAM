import sqlite3

def inspect_triggers():
    try:
        conn = sqlite3.connect('../data/gestor3d.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='trigger'")
        triggers = cursor.fetchall()
        
        print(f"Found {len(triggers)} triggers:")
        for name, table, sql in triggers:
            print(f"\nTrigger: {name}")
            print(f"Table: {table}")
            print(f"SQL: {sql}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_triggers()
