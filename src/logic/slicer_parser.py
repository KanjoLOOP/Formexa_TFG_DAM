import re
import os

class SlicerParser:
    """
    Clase para analizar archivos G-code y extraer metadatos como tiempo de impresión y uso de filamento.
    Soporta Cura y PrusaSlicer (y derivados como OrcaSlicer/BambuStudio).
    """
    
    def parse_file(self, file_path):
        """
        Analiza un archivo G-code y devuelve un diccionario con los metadatos encontrados.
        
        Args:
            file_path (str): Ruta al archivo G-code.
            
        Returns:
            dict: Diccionario con claves 'print_time_seconds', 'filament_weight_g', 'filament_length_m', 'slicer_name'.
                  Devuelve None si no se pudo analizar o no se encontraron datos relevantes.
        """
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Leemos solo las primeras y últimas líneas para eficiencia, 
                # ya que los metadatos suelen estar ahí.
                # Pero algunos slicers ponen info al final.
                # Para estar seguros leemos todo, pero los archivos pueden ser grandes.
                # Estrategia: Leer primeras 500 líneas y últimas 500 líneas.
                
                content_head = ""
                for _ in range(500):
                    line = f.readline()
                    if not line: break
                    content_head += line
                
                # Ir al final para leer el footer
                f.seek(0, 2) # End of file
                file_size = f.tell()
                
                # Si el archivo es pequeño, ya lo leímos casi todo, pero si es grande leemos el final
                content_tail = ""
                if file_size > 10000: # Arbitrario
                    seek_pos = max(0, file_size - 10000) # Leer últimos 10KB
                    f.seek(seek_pos)
                    content_tail = f.read()
                
                full_content_sample = content_head + "\n" + content_tail
                
                # Intentar detectar slicer y extraer datos
                data = self._parse_cura(full_content_sample)
                if not data:
                    data = self._parse_prusa(full_content_sample)
                
                # Si tenemos longitud pero no peso, estimar peso (PLA 1.75mm por defecto)
                if data and 'filament_length_m' in data and 'filament_weight_g' not in data:
                    data['filament_weight_g'] = self._estimate_weight_from_length(data['filament_length_m'])
                
                return data
                
        except Exception as e:
            print(f"Error parsing G-code: {e}")
            return None

    def _estimate_weight_from_length(self, length_m, diameter_mm=1.75, density_g_cm3=1.24):
        """
        Estima el peso en gramos basado en la longitud en metros.
        Por defecto usa PLA (1.24 g/cm3) y 1.75mm.
        """
        import math
        radius_cm = (diameter_mm / 10) / 2
        length_cm = length_m * 100
        volume_cm3 = math.pi * (radius_cm ** 2) * length_cm
        return volume_cm3 * density_g_cm3

    def _parse_cura(self, content):
        """Analiza formato de Cura."""
        # Cura suele poner:
        # ;TIME:6666
        # ;Filament used: 1.23m
        # ;Filament weight: 3.45g (A veces no está explícito en versiones viejas, pero sí la longitud)
        
        data = {}
        
        # Tiempo (segundos)
        time_match = re.search(r';TIME:(\d+)', content)
        if time_match:
            data['print_time_seconds'] = int(time_match.group(1))
            data['slicer_name'] = 'Cura'
        
        # Longitud filamento (metros)
        len_match = re.search(r';Filament used: ([\d.]+)m', content)
        if len_match:
            data['filament_length_m'] = float(len_match.group(1))
            data['slicer_name'] = 'Cura'

        # Peso filamento (gramos) - A veces Cura pone ";Filament weight = 12.34g" o similar en plugins
        # Pero estándar suele ser longitud. Podemos estimar peso si tenemos densidad (PLA ~1.24g/cm3) y diámetro (1.75mm).
        # Por ahora extraemos si existe explícito.
        weight_match = re.search(r';Filament weight: ([\d.]+)g', content)
        if weight_match:
            data['filament_weight_g'] = float(weight_match.group(1))
        
        if 'print_time_seconds' in data:
            return data
        return None

    def _parse_prusa(self, content):
        """Analiza formato de PrusaSlicer / SuperSlicer / OrcaSlicer / BambuStudio."""
        # PrusaSlicer pone al final:
        # ; estimated printing time = 1h 23m 45s
        # ; filament used [mm] = 1234.56
        # ; filament used [cm3] = 1.23
        # ; filament used [g] = 12.34
        # ; total filament cost = 1.23
        
        data = {}
        
        # Tiempo
        # Formato: 1h 23m 45s o 23m 45s o 45s
        time_match = re.search(r'; estimated printing time = (.*)', content)
        if time_match:
            time_str = time_match.group(1).strip()
            data['print_time_seconds'] = self._parse_time_str(time_str)
            data['slicer_name'] = 'PrusaSlicer/Derivados'
            
        # Peso
        weight_match = re.search(r'; filament used \[g\] = ([\d.]+)', content)
        if weight_match:
            data['filament_weight_g'] = float(weight_match.group(1))
            
        # Longitud (mm) -> convertir a m
        len_match = re.search(r'; filament used \[mm\] = ([\d.]+)', content)
        if len_match:
            data['filament_length_m'] = float(len_match.group(1)) / 1000.0
            
        if 'print_time_seconds' in data:
            return data
        return None

    def _parse_time_str(self, time_str):
        """Convierte string de tiempo tipo '1h 23m 45s' a segundos."""
        total_seconds = 0
        
        # Días
        d_match = re.search(r'(\d+)d', time_str)
        if d_match:
            total_seconds += int(d_match.group(1)) * 86400
            
        # Horas
        h_match = re.search(r'(\d+)h', time_str)
        if h_match:
            total_seconds += int(h_match.group(1)) * 3600
            
        # Minutos
        m_match = re.search(r'(\d+)m', time_str)
        if m_match:
            total_seconds += int(m_match.group(1)) * 60
            
        # Segundos
        s_match = re.search(r'(\d+)s', time_str)
        if s_match:
            total_seconds += int(s_match.group(1))
            
        return total_seconds
