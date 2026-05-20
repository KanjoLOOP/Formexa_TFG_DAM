import subprocess
import sys

subprocess.check_call([sys.executable, '-m', 'PyInstaller', '--clean', 'Formexa3D.spec'])
