from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import art3d
import trimesh
import numpy as np
from src.utils.logger import logger

class Viewer3DWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0) # Sin márgenes para inmersión
        self.setLayout(self.layout)
        
        # Fondo oscuro suave (casi negro pero no #000)
        self.figure = Figure(figsize=(5, 5), dpi=100, facecolor='#1e1e1e')
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.configure_axes()

    def configure_axes(self):
        self.ax.set_facecolor('#1e1e1e')
        
        # Eliminar grid y paneles antiguos
        self.ax.grid(False)
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        self.ax.xaxis.pane.set_edgecolor('none')
        self.ax.yaxis.pane.set_edgecolor('none')
        self.ax.zaxis.pane.set_edgecolor('none')
        
        # Eliminar ticks y etiquetas de ejes para limpieza total
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_zticks([])
        
        # Dibujar ejes minimalistas manualmente en el origen (0,0,0)
        # Eje X (Rojo), Eje Y (Verde), Eje Z (Azul)
        len_axis = 40
        self.ax.plot([0, len_axis], [0, 0], [0, 0], color='#ff4d4d', linewidth=2) # X
        self.ax.plot([0, 0], [0, len_axis], [0, 0], color='#4dff4d', linewidth=2) # Y
        self.ax.plot([0, 0], [0, 0], [0, len_axis], color='#4d4dff', linewidth=2) # Z
        
        # Ajustar límites iniciales
        self.ax.set_xlim(-100, 100)
        self.ax.set_ylim(-100, 100)
        self.ax.set_zlim(0, 200)

        # Vista isométrica inicial agradable
        self.ax.view_init(elev=25, azim=45)

    def draw_shadow_blob(self):
        """Dibuja una sombra suave en el suelo (Z=0)."""
        # Círculo semitransparente negro en Z=0
        p = np.linspace(0, 2*np.pi, 50)
        r = 80
        x = r * np.cos(p)
        y = r * np.sin(p)
        z = np.zeros_like(x)
        self.ax.plot(x, y, z, color='black', alpha=0.1)
        
        # Relleno de la sombra
        verts = [list(zip(x, y, z))]
        poly = art3d.Poly3DCollection(verts, alpha=0.15)
        poly.set_facecolor('black')
        poly.set_edgecolor('none')
        self.ax.add_collection3d(poly)

    def load_model(self, file_path):
        """Carga y renderiza un archivo STL."""
        self.ax.clear()
        self.configure_axes()
        self.draw_shadow_blob() # Añadir sombra base
        
        try:
            mesh = trimesh.load(file_path)
            
            if isinstance(mesh, trimesh.Scene):
                if len(mesh.geometry) > 0:
                    mesh = list(mesh.geometry.values())[0]
                else:
                    return

            if len(mesh.faces) > 5000:
                mesh = mesh.simplify_quadratic_decimation(5000)

            vertices = mesh.vertices
            faces = mesh.faces

            # Material moderno: Gris metálico suave con bordes muy sutiles
            poly3d = art3d.Poly3DCollection(vertices[faces], alpha=0.9)
            poly3d.set_facecolor('#cfcfcf') # Gris claro para mejor contraste con fondo oscuro
            poly3d.set_edgecolor('#2a2a2a') # Bordes oscuros sutiles
            poly3d.set_linewidth(0.05) # Líneas muy finas

            self.ax.add_collection3d(poly3d)

            # Auto-escalado y centrado
            scale = vertices.flatten()
            self.ax.auto_scale_xyz(scale, scale, scale)
            
            # Ajustar límites para que el modelo quede sobre la sombra (Z>=0)
            # Esto es aproximado, matplotlib centra la vista
            
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error al cargar modelo: {e}")
            self.ax.text(0, 0, 0, "Error", color='#ff6b6b', ha='center')
            self.canvas.draw()
