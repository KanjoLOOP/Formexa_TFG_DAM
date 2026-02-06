import sqlite3
import os

def fix_filaments_table():
    db_path = '../data/gestor3d.db'
    
    # Backup first
    backup_path = '../data/gestor3d_backup_filaments.db'
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✓ Backup created: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Ver datos actuales
        cursor.execute("SELECT COUNT(*) FROM filaments")
        count = cursor.fetchone()[0]
        print(f"\nCurrent filaments count: {count}")
        
        # 2. Guardar datos en tabla temporal
        print("\n1. Creating backup table...")
        cursor.execute("""
            CREATE TABLE filaments_backup AS 
            SELECT * FROM filaments
        """)
        
        # 3. Eliminar tabla original
        print("2. Dropping original table...")
        cursor.execute("DROP TABLE filaments")
        
        # 4. Recrear tabla SIN la foreign key a users_old
        print("3. Creating new table without users_old reference...")
        cursor.execute("""
            CREATE TABLE filaments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                material_type TEXT NOT NULL,
                color TEXT,
                weight_initial REAL NOT NULL,
                weight_current REAL NOT NULL,
                price REAL NOT NULL,
                diameter REAL DEFAULT 1.75,
                density REAL DEFAULT 1.24,
                purchase_date DATE,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # 5. Restaurar datos
        print("4. Restoring data...")
        cursor.execute("""
            INSERT INTO filaments 
            SELECT * FROM filaments_backup
        """)
        
        # 6. Eliminar backup temporal
        print("5. Cleaning up...")
        cursor.execute("DROP TABLE filaments_backup")
        
        # 7. Verificar
        cursor.execute("SELECT COUNT(*) FROM filaments")
        new_count = cursor.fetchone()[0]
        print(f"\n✓ New filaments count: {new_count}")
        
        if new_count == count:
            print("✓ All data preserved successfully!")
        else:
            print(f"⚠️  Warning: Data count mismatch ({count} -> {new_count})")
        
        # Verificar foreign keys
        cursor.execute("PRAGMA foreign_key_list(filaments)")
        fks = cursor.fetchall()
        print(f"\nForeign keys in new table: {len(fks)}")
        for fk in fks:
            print(f"  - {fk}")
        
        conn.commit()
        print("\n✅ TABLE FIXED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_filaments_table()
