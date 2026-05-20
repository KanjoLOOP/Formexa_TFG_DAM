import pytest
from src.logic.cost_calculator import CostCalculator


@pytest.fixture
def calc():
    return CostCalculator()


def test_filament_cost(calc):
    assert calc.calculate_filament_cost(100, 20) == pytest.approx(2.0)


def test_energy_cost(calc):
    assert calc.calculate_energy_cost(200, 1, 0.15) == pytest.approx(0.03)


def test_total_cost(calc):
    total = calc.calculate_total_cost(filament_cost=2.0, energy_cost=0.03, additional_costs=0)
    assert total == pytest.approx(2.03)


def test_zero_weight_filament_cost(calc):
    assert calc.calculate_filament_cost(0, 20) == pytest.approx(0.0)


def test_zero_time_energy_cost(calc):
    assert calc.calculate_energy_cost(200, 0, 0.15) == pytest.approx(0.0)
