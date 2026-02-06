import sqlite3
import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.db_manager import DBManager

def test_insert():
    try:
        # Test directo con sqlite3
        print("=== Test 1: Direct sqlite3 ===")
        conn = sqlite3.connect('../data/gestor3d.db')
        cursor = conn.cursor()
        
        query = """
            INSERT INTO filaments (brand, material_type, color, weight_initial, weight_current, price, diameter, density)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = ("TestBrand", "PLA", "Red", 1000, 1000, 20.0, 1.75, 1.24)
        
        cursor.execute(query, params)
        conn.commit()
        print("✓ Direct insert successful")
        
        # Limpiar
        cursor.execute("DELETE FROM filaments WHERE brand='TestBrand'")
        conn.commit()
        conn.close()
        
        # Test con DBManager
        print("\n=== Test 2: Using DBManager ===")
        db = DBManager()
        result = db.execute_query(query, params)
        print(f"✓ DBManager insert result: {result}")
        
        # Limpiar
        db.execute_query("DELETE FROM filaments WHERE brand='TestBrand'")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_insert()
