import os
import subprocess
import sys
from PIL import Image

def create_icon(source_image_path, icon_path):
    """Convierte una imagen (PNG) a formato ICO."""
    try:
        img = Image.open(source_image_path)
        img.save(icon_path, format='ICO', sizes=[(256, 256)])
        print(f"Icono creado exitosamente en: {icon_path}")
        return True
    except Exception as e:
        print(f"Error al crear el icono: {e}")
        return False

def run_pyinstaller():
    """Ejecuta PyInstaller para crear el ejecutable."""
    # Definir rutas
    project_dir = os.getcwd()
    main_script = os.path.join(project_dir, 'src', 'main.py')
    icon_path = os.path.join(project_dir, 'assets', 'app_icon.ico')
    
    # Verificar si el icono existe
    if not os.path.exists(icon_path):
        print(f"Advertencia: No se encontró el icono en {icon_path}. Se usará el icono por defecto.")
        icon_arg = []
    else:
        icon_arg = [f'--icon={icon_path}']

    # Datos adicionales (carpeta assets y schema.sql)
    # En Windows el separador es ;
    # assets -> assets
    # src/database/schema.sql -> src/database
    add_data_arg = f'assets{os.pathsep}assets{os.pathsep}src/database/schema.sql{os.pathsep}src/database'

    # Comando de PyInstaller
    # --noconsole: No mostrar consola (para GUI)
    # --onefile: Un solo archivo ejecutable
    # --clean: Limpiar caché
    # --name: Nombre del ejecutable
    command = [
        sys.executable, '-m', 'PyInstaller',
        '--noconsole',
        '--onefile',
        '--clean',
        '--name=Formexa3D',
        '--name=Formexa3D',
        '--add-data=assets;assets',
        '--add-data=src/database/schema.sql;src/database',
        '--add-data=src/locales;src/locales',
        *icon_arg,
        main_script
    ]

    print("Ejecutando PyInstaller con el siguiente comando:")
    print(" ".join(command))

    try:
        subprocess.check_call(command)
        print("\n¡Construcción completada con éxito!")
        dist_exe_path = os.path.join(project_dir, 'dist', 'Formexa3D.exe')
        root_exe_path = os.path.join(project_dir, 'Formexa3D.exe')
        
        print(f"El ejecutable se encuentra en: {dist_exe_path}")
        
        # Copiar al directorio raíz
        import shutil
        shutil.copy2(dist_exe_path, root_exe_path)
        print(f"¡Copiado al directorio raíz! Ahora tienes el ejecutable aquí: {root_exe_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"\nError durante la ejecución de PyInstaller: {e}")
    except Exception as e:
        print(f"\nError al copiar el ejecutable: {e}")

if __name__ == "__main__":
    # Ruta de la imagen subida (ajusta esto si cambia)
    uploaded_image_path = r'C:/Users/Ebisu/.gemini/antigravity/brain/36e88bcb-dd48-4b3f-b39a-a7e4a2fb83d5/uploaded_image_1769170849821.png'
    
    # Asegurar que existe la carpeta assets
    if not os.path.exists('assets'):
        os.makedirs('assets')
        
    target_icon_path = os.path.join('assets', 'app_icon.ico')

    # 1. Crear icono
    if os.path.exists(uploaded_image_path):
        create_icon(uploaded_image_path, target_icon_path)
    else:
        print(f"No se encontró la imagen subida en: {uploaded_image_path}")
        # Si no está la imagen, preguntamos si continuar? O simplemente intentamos construir sin icono nuevo
        print("Intentando construir sin actualizar el icono...")

    # 2. Correr PyInstaller
    run_pyinstaller()
