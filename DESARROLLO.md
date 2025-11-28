# Documentación de Desarrollo - Gestor 3D

## Registro de Cambios

### Versión 0.2.0 (28/11/2025)

#### Autenticación y Seguridad
- ✅ Sistema de Login y Registro de usuarios
- ✅ Gestión de sesiones con `AuthManager`
- ✅ **Modo Invitado**: Implementación de restricciones de acceso en `MainWindow`
- ✅ Hashing de contraseñas con SHA-256

#### Nuevas Funcionalidades
- ✅ **Integración con Slicers**:
  - Clase `SlicerParser` para analizar G-code
  - Soporte para Cura (tiempo, longitud) y PrusaSlicer (tiempo, peso, coste)
  - Estimación inteligente de peso basada en longitud
- ✅ **Exportación PDF**:
  - Clase `ReportGenerator` usando `reportlab`
  - Generación de informes de costes profesionales
- ✅ **Mejoras en UI**:
  - Botón de importación en Calculadora
  - Pestaña de Configuración funcional

---

### Versión 0.1.0 (26/11/2025)

#### Configuración Inicial
- ✅ Inicialización del repositorio Git
- ✅ Creación de estructura de directorios modular
- ✅ Configuración de dependencias (requirements.txt)
- ✅ Migración de MySQL a SQLite por simplicidad de desarrollo

#### Base de Datos (SQLite)
- ✅ Diseño del esquema E-R con 4 tablas principales:
  - `users`: Gestión de usuarios
  - `filaments`: Inventario de materiales
  - `models`: Biblioteca de archivos STL
  - `projects`: Proyectos de impresión
- ✅ Implementación de `DBManager` con métodos CRUD
- ✅ Inicialización automática de base de datos

#### Interfaz Gráfica (PyQt5)
- ✅ Ventana principal con navegación lateral
- ✅ Sistema de estilos QSS (Dark Mode)
- ✅ Arquitectura basada en QStackedWidget para navegación fluida

#### Módulos Implementados

##### 1. Calculadora de Costes
- **Lógica**: Clase `CostCalculator` con métodos de cálculo
- **UI**: Formulario con validación de entradas
- **Funcionalidades**:
  - Cálculo de coste de filamento (peso × precio/kg)
  - Cálculo de coste energético (potencia × tiempo × tarifa)
  - Coste total agregado
  - **[NUEVO]** Importación de G-code y Exportación PDF

##### 2. Biblioteca y Visor 3D
- **Lógica**: `LibraryManager` para gestión de archivos STL
- **Visor**: Integración de Matplotlib 3D con Trimesh
- **Funcionalidades**:
  - Importación de archivos STL
  - Visualización 3D embebida
  - Gestión de modelos (añadir/eliminar)
  - Almacenamiento en carpeta `assets/models/`

##### 3. Inventario de Filamentos
- **Lógica**: `InventoryManager` con CRUD completo
- **UI**: Tabla interactiva + formulario de registro
- **Funcionalidades**:
  - Registro de rollos (marca, tipo, color, peso, precio)
  - Visualización en tabla
  - Eliminación de registros

##### 4. Marketplace
- **UI**: Grid de tarjetas con modelos simulados
- **Funcionalidades**:
  - Catálogo de modelos 3D
  - Simulación de compra/descarga

## Arquitectura del Código

```
Gestor3D/
├── src/
│   ├── main.py              # Punto de entrada
│   ├── database/
│   │   ├── schema.sql       # Esquema SQLite
│   │   └── db_manager.py    # Gestor de conexión
│   ├── logic/
│   │   ├── cost_calculator.py
│   │   ├── library_manager.py
│   │   ├── inventory_manager.py
│   │   ├── auth_manager.py  # [NUEVO] Gestor de auth
│   │   ├── slicer_parser.py # [NUEVO] Parser G-code
│   │   └── report_generator.py # [NUEVO] Generador PDF
│   └── ui/
│       ├── main_window.py
│       ├── home_widget.py
│       ├── calculator_widget.py
│       ├── library_widget.py
│       ├── inventory_widget.py
│       ├── marketplace_widget.py
│       ├── login_widget.py  # [NUEVO]
│       └── viewer_3d.py
├── assets/
│   ├── styles.qss           # Estilos globales
│   └── models/              # Biblioteca de STL
├── gestor3d.db              # Base de datos SQLite
└── requirements.txt
```

## Decisiones Técnicas

### SQLite vs MySQL
Se optó por SQLite en lugar de MySQL debido a:
- Cero configuración (no requiere servidor)
- Portabilidad (archivo único)
- Ideal para aplicaciones de escritorio monousuario
- Facilita el desarrollo y despliegue

### Matplotlib vs PyOpenGL
Se eligió Matplotlib para el visor 3D porque:
- Integración nativa con PyQt5
- Menor curva de aprendizaje
- Suficiente para visualización estática de modelos
- Renderizado adecuado para archivos STL simplificados

## Próximas Mejoras
- [ ] Marketplace real con API externa
- [ ] Gráficos de consumo y estadísticas avanzados
- [ ] Sincronización en la nube
- [ ] Sistema de plugins

