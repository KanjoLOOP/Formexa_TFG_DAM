import unittest
import os
import sys

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logic.slicer_parser import SlicerParser

class TestSlicerParser(unittest.TestCase):
    def setUp(self):
        self.parser = SlicerParser()
        self.cura_content = """
;FLAVOR:Marlin
;TIME:3665
;Filament used: 1.23m
;Layer height: 0.2
;MINX:10.5
;MINY:10.5
;MINZ:0.2
;MAXX:189.5
;MAXY:189.5
;MAXZ:20.0
;Generated with Cura_SteamEngine 4.8.0
"""
        self.prusa_content = """
G1 X10 Y10 E1
; ... G-code content ...
; estimated printing time = 1h 23m 45s
; filament used [mm] = 1234.56
; filament used [cm3] = 1.23
; filament used [g] = 12.34
; total filament cost = 0.25
"""
        self.prusa_no_weight_content = """
G1 X10 Y10 E1
; estimated printing time = 45m 0s
; filament used [mm] = 1000.00
"""

    def test_cura_parsing(self):
        # Create temp file
        with open("test_cura.gcode", "w") as f:
            f.write(self.cura_content)
            
        data = self.parser.parse_file("test_cura.gcode")
        self.assertIsNotNone(data)
        self.assertEqual(data['print_time_seconds'], 3665)
        self.assertEqual(data['filament_length_m'], 1.23)
        self.assertEqual(data['slicer_name'], 'Cura')
        # Check estimated weight (1.23m * ~3g/m for 1.75mm PLA is roughly 3.7g)
        # 1.23m = 123cm. r=0.0875cm. Vol = pi * r^2 * h = 3.14159 * 0.007656 * 123 = 2.95 cm3.
        # Weight = 2.95 * 1.24 = 3.66g
        self.assertAlmostEqual(data['filament_weight_g'], 3.66, delta=0.1)
        
        os.remove("test_cura.gcode")

    def test_prusa_parsing(self):
        with open("test_prusa.gcode", "w") as f:
            f.write(self.prusa_content)
            
        data = self.parser.parse_file("test_prusa.gcode")
        self.assertIsNotNone(data)
        # 1h 23m 45s = 3600 + 1380 + 45 = 5025s
        self.assertEqual(data['print_time_seconds'], 5025)
        self.assertEqual(data['filament_weight_g'], 12.34)
        self.assertAlmostEqual(data['filament_length_m'], 1.23456, places=4)
        
        os.remove("test_prusa.gcode")

    def test_prusa_estimation(self):
        with open("test_prusa_est.gcode", "w") as f:
            f.write(self.prusa_no_weight_content)
            
        data = self.parser.parse_file("test_prusa_est.gcode")
        self.assertIsNotNone(data)
        self.assertEqual(data['print_time_seconds'], 2700) # 45m
        # 1m length -> ~2.98g
        self.assertAlmostEqual(data['filament_weight_g'], 2.98, delta=0.1)
        
        os.remove("test_prusa_est.gcode")

if __name__ == '__main__':
    unittest.main()
