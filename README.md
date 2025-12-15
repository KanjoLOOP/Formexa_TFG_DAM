# Formexa

![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow)
![Versión](https://img.shields.io/badge/Versión-0.1.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)

## Descripción
**Formexa** es una aplicación de escritorio multiplataforma diseñada para entusiastas y profesionales de la impresión 3D. Permite gestionar proyectos, calcular costes de impresión, organizar una biblioteca de modelos con visualización 3D integrada, controlar el inventario de filamentos y acceder a un marketplace de diseños.

## Objetivos del Proyecto
- **Gestión Integral**: Centralizar proyectos, materiales y costes en una sola aplicación
- **Calculadora de Costes**: Estimación precisa basada en material, energía y tiempo
- **Biblioteca 3D**: Organización visual de archivos STL con visor integrado
- **Inventario**: Control de stock de filamentos con registro detallado
- **Marketplace**: Plataforma de intercambio de modelos (simulado)

## Características

### Autenticación y Seguridad
- Sistema de Login y Registro
- **Modo Invitado**: Acceso limitado a la Calculadora y Configuración
- Gestión de sesiones de usuario

### Calculadora de Costes
- Cálculo automático de coste de filamento
- **Importación de G-code**: Carga automática de datos desde Cura y PrusaSlicer
- Estimación de consumo energético
- **Exportación a PDF**: Generación de informes detallados
- Desglose detallado de gastos

### Biblioteca de Modelos
- Importación de archivos STL
- Visor 3D integrado (Matplotlib + Trimesh)
- Gestión de modelos (añadir/eliminar)

### Inventario de Filamentos
- Registro de rollos (marca, tipo, color, peso, precio)
- Tabla interactiva con búsqueda
- Control de stock restante

### Marketplace
- Catálogo de modelos 3D
- Simulación de compra/descarga

### Notificaciones Inteligentes
- Panel de alertas en el Dashboard
- Aviso de filamentos con poco material (<20%)
- Resumen de actividad mensual y modelos recientes

## Tecnologías
- **Lenguaje**: Python 3.8+
- **Interfaz**: PyQt5
- **Base de Datos**: SQLite
- **Visualización 3D**: Trimesh + Matplotlib

## Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip

### Pasos
```bash
# Clonar el repositorio
git clone https://github.com/KanjoLOOP/TFG_DAM.git
cd Formexa

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python src/main.py
```

## Documentación
- [Manual de Usuario](docs/MANUAL_USUARIO.md) - Guía completa de uso
- [Documentación de Desarrollo](docs/DESARROLLO.md) - Arquitectura y decisiones técnicas
- [Fundamentos Teóricos](docs/DOCUMENTACION.md) - Objetivos y metodología

## Estructura del Proyecto
```
Formexa/
├── src/
│   ├── main.py              # Punto de entrada
│   ├── database/            # Esquema y gestor de BD
│   ├── logic/               # Lógica de negocio
│   └── ui/                  # Interfaces gráficas
├── assets/
│   ├── styles.qss           # Estilos
│   └── models/              # Biblioteca de STL
├── docs/
│   ├── MANUAL_USUARIO.md
│   ├── DESARROLLO.md
│   └── DOCUMENTACION.md
└── requirements.txt
```

## Estado del Proyecto
**Versión Actual**: 0.2.0 (Beta)

### Completado 
- [x] Interfaz gráfica con navegación
- [x] Calculadora de costes funcional
- [x] Biblioteca con visor 3D
- [x] Inventario CRUD
- [x] Marketplace simulado
- [x] Dashboard con notificaciones inteligentes
- [x] Autenticación de usuarios y Modo Invitado
- [x] Exportación de informes PDF
- [x] Integración con slicers (Cura, PrusaSlicer)

### Próximas Mejoras 
- [ ] Marketplace real con API
- [ ] Gráficos de estadísticas avanzados
- [ ] Sincronización en la nube

##  Autor
Desarrollado como Trabajo de Fin de Grado (TFG) - DAM


