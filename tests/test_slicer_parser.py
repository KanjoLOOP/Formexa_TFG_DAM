import pytest
from src.logic.slicer_parser import SlicerParser

CURA_CONTENT = """;FLAVOR:Marlin
;TIME:3665
;Filament used: 1.23m
;Layer height: 0.2
;Generated with Cura_SteamEngine 4.8.0
"""

PRUSA_CONTENT = """G1 X10 Y10 E1
; estimated printing time = 1h 23m 45s
; filament used [mm] = 1234.56
; filament used [cm3] = 1.23
; filament used [g] = 12.34
; total filament cost = 0.25
"""

PRUSA_NO_WEIGHT = """G1 X10 Y10 E1
; estimated printing time = 45m 0s
; filament used [mm] = 1000.00
"""


def test_cura_parsing(tmp_path):
    f = tmp_path / "cura.gcode"
    f.write_text(CURA_CONTENT)
    data = SlicerParser().parse_file(str(f))
    assert data is not None
    assert data['print_time_seconds'] == 3665
    assert data['filament_length_m'] == pytest.approx(1.23)
    assert data['slicer_name'] == 'Cura'
    assert data['filament_weight_g'] == pytest.approx(3.66, abs=0.1)


def test_prusa_parsing(tmp_path):
    f = tmp_path / "prusa.gcode"
    f.write_text(PRUSA_CONTENT)
    data = SlicerParser().parse_file(str(f))
    assert data is not None
    assert data['print_time_seconds'] == 5025  # 1h 23m 45s
    assert data['filament_weight_g'] == pytest.approx(12.34)
    assert data['filament_length_m'] == pytest.approx(1.23456, abs=1e-4)


def test_prusa_estimation(tmp_path):
    f = tmp_path / "est.gcode"
    f.write_text(PRUSA_NO_WEIGHT)
    data = SlicerParser().parse_file(str(f))
    assert data is not None
    assert data['print_time_seconds'] == 2700  # 45m
    assert data['filament_weight_g'] == pytest.approx(2.98, abs=0.1)
