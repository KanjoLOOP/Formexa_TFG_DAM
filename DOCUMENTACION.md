# Documentación del Proyecto: Gestor 3D

## 1. Objetivos

### Objetivo General
Desarrollar una aplicación de escritorio multiplataforma que permita a los usuarios de impresoras 3D gestionar sus proyectos, materiales y costes de forma completa, utilizando una base de datos robusta y una interfaz moderna.

### Objetivos Específicos
- **Calculadora de Costes**: Implementar un sistema que estime el gasto total de cada impresión considerando precio del filamento, consumo energético y tiempo.
- **Biblioteca de Diseños**: Crear un repositorio local para almacenar, visualizar y gestionar archivos STL con metadatos y miniaturas.
- **Visor 3D**: Integrar visualización de modelos (STL) mediante librerías como Trimesh, Pyglet u Open3D.
- **Inventario**: Módulo para registrar rollos de filamento (peso, precio, fabricante, remanente).
- **Marketplace**: Función para simular compra/venta de modelos 3D.
- **Persistencia**: Uso de SQLite para garantizar portabilidad y simplicidad.
- **Interfaz**: Diseño moderno e intuitivo con PyQt5.

## 2. Fundamentos Teóricos

### Tecnologías Seleccionadas
- **Python 3**: Elegido por su versatilidad y amplio ecosistema.
- **PyQt5**: Framework robusto para interfaces de escritorio modernas.
- **SQLite**: Base de datos relacional ligera y sin servidor, ideal para escritorio.
- **Librerías 3D**: Trimesh y Matplotlib para el procesamiento y renderizado de geometría 3D.
- **ReportLab**: Para la generación profesional de informes PDF.

### Metodología
El desarrollo seguirá un enfoque **Ágil (SCRUM)**, con entregas incrementales:
1.  Diseño de Interfaz.
2.  Base de Datos.
3.  Cálculo de Costes.
4.  Biblioteca y Visor.
5.  Inventario.
6.  Marketplace.
7.  Pruebas.

## 3. Materiales y Métodos

### Fases de Desarrollo
1.  **Diseño UI**: Adaptación de plantilla moderna.
2.  **Backend DB**: Creación de esquema MySQL y conexión.
3.  **Lógica de Costes**: Implementación de algoritmos de cálculo.
4.  **Visualización**: Integración del motor de renderizado 3D.
5.  **Gestión de Datos**: Desarrollo del módulo de inventario.
6.  **Integración**: Conexión de todos los módulos y marketplace.
7.  **QA**: Pruebas funcionales y de usabilidad.
