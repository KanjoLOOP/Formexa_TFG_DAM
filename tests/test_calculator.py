import unittest
import sys
import os

# Asegurar path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logic.cost_calculator import CostCalculator

class TestCostCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = CostCalculator()

    def test_calculate_filament_cost(self):
        # 100g, 20€/kg -> 20 * (100/1000) = 2€
        cost = self.calculator.calculate_filament_cost(100, 20)
        self.assertAlmostEqual(cost, 2.0)

    def test_calculate_energy_cost(self):
        # 200W, 1 hour, 0.15€/kWh -> (200/1000) * 1 * 0.15 = 0.03€
        cost = self.calculator.calculate_energy_cost(200, 1, 0.15)
        self.assertAlmostEqual(cost, 0.03)

    def test_total_cost(self):
        # 2€ material + 0.03€ energia = 2.03
        total = self.calculator.calculate_total_cost(filament_cost=2.0, energy_cost=0.03, additional_costs=0)
        self.assertAlmostEqual(total, 2.03)

if __name__ == '__main__':
    unittest.main()
