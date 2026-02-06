import unittest
import sys
import os
from unittest.mock import MagicMock

# Asegurar path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logic.inventory_manager import InventoryManager

class TestInventoryManager(unittest.TestCase):
    def setUp(self):
        self.manager = InventoryManager()
        # Mock de DB para no tocar base de datos real
        self.manager.db = MagicMock()

    def test_add_filament_valid(self):
        self.manager.db.execute_query.return_value = True
        success, msg = self.manager.add_filament("Brand", "PLA", "Red", 1000, 20.0)
        self.assertTrue(success)
        self.assertIn("correctamente", msg)

    def test_add_filament_invalid(self):
        # Peso negativo
        success, msg = self.manager.add_filament("Brand", "PLA", "Red", -10, 20.0)
        self.assertFalse(success)
        
    def test_get_all_filaments(self):
        self.manager.db.fetch_query.return_value = [
            {'id': 1, 'brand': 'BrandA'},
            {'id': 2, 'brand': 'BrandB'}
        ]
        filaments = self.manager.get_all_filaments()
        self.assertEqual(len(filaments), 2)
        self.assertEqual(filaments[0]['brand'], 'BrandA')

if __name__ == '__main__':
    unittest.main()
