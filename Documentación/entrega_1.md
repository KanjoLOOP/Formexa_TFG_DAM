ENTREGA 1: PLANIFICACIÓN Y METODOLOGÍA DEL PROYECTO

1. METODOLOGÍA DEL TRABAJO

Para el desarrollo de la aplicación Gestor3D, se ha optado por una metodología de desarrollo de software ágil e iterativa, lo que permite una adaptación flexible a los cambios y una mejora continua del producto.

1.1. Enfoque de Desarrollo

El proyecto se ha dividido en pequeños ciclos de desarrollo o sprints, donde en cada uno se abordan funcionalidades específicas, se implementan, se prueban y se refinan.

- Análisis de Requisitos: Identificación de las necesidades del usuario (gestión de inventario 3D, control de filamentos, costes, etc.).
- Diseño Modular: Se sigue una arquitectura basada en componentes, separando claramente:
    - Interfaz de Usuario (UI): Desarrollada con PyQt5, garantizando una experiencia visual moderna y funcional.
    - Lógica de Negocio: Scripts en Python que gestionan las operaciones y cálculos.
    - Persistencia de Datos: Uso de SQLite para un almacenamiento local ligero y eficiente.
- Control de Versiones: Se utiliza Git para el control de versiones, alojando el código en un repositorio remoto (GitHub). Esto permite mantener un historial de cambios seguro y facilita la colaboración.
- Integración Continua (CI/CD): Se ha implementado un flujo de trabajo con GitHub Actions para automatizar la construcción del ejecutable y la generación del instalador de Windows, asegurando que siempre haya una versión distribuible funcional.

1.2. Herramientas Utilizadas

- IDE: Visual Studio Code.
- Lenguaje: Python 3.12.
- Framework Gráfico: PyQt5.
- Base de Datos: SQLite.
- Empaquetado: PyInstaller e Inno Setup (automátizado en la nube).


2. CALENDARIZACIÓN DEL TRABAJO

A continuación, se detalla la planificación estimada para el desarrollo del TFG, dividida por fases y semanas.

Fase I: Planificación (Semanas 1-2)
- Definición del alcance y objetivos.
- Selección de tecnologías (Python, PyQt).
- Auditoría inicial y configuración del entorno.

Fase II: Diseño (Semanas 3-4)
- Diseño del esquema de la base de datos (ER).
- Bocetos y diseño de la interfaz de usuario (UI).
- Definición de la estructura del proyecto (MVC).

Fase III: Implementación Core (Semanas 5-7)
- Desarrollo del módulo de Inventario y CRUD.
- Implementación de la gestión de proyectos y costes.
- Integración de la visualización de datos.

Fase IV: Refinamiento (Semanas 8-9)
- Integración de gráficos y estadísticas.
- Implementación del sistema de logs y auditoría.
- Traducción y localización (i18n).

Fase V: Despliegue y Pruebas (Semana 10)
- Configuración del instalador (Inno Setup).
- Pruebas unitarias y de sistema.
- Configuración de GitHub Actions para CI/CD.

Fase VI: Documentación (Semanas 11-12)
- Redacción de la memoria del proyecto.
- Elaboración de manuales de usuario.
- Preparación de la presentación final.


3. BIBLIOGRAFÍA Y REFERENCIAS

Para el desarrollo de este proyecto se han consultado las siguientes fuentes de documentación técnica y recursos:

3.1. Documentación Oficial

- Python Software Foundation. Python 3.12 Documentation.
  Disponible en: https://docs.python.org/3/

- Riverbank Computing. PyQt5 Reference Guide.
  Disponible en: https://www.riverbankcomputing.com/static/Docs/PyQt5/

- SQLite. SQLite Documentation.
  Disponible en: https://www.sqlite.org/docs.html

3.2. Herramientas y Librerías

- PyInstaller. PyInstaller Manual.
  Disponible en: https://pyinstaller.org/en/stable/

- Inno Setup. Inno Setup Help.
  Disponible en: https://jrsoftware.org/ishelp/

- GitHub. GitHub Actions Documentation.
  Disponible en: https://docs.github.com/en/actions

3.3. Recursos Adicionales

- Stack Overflow: Consultas variables sobre patrones de diseño con PyQt y optimización de bases de datos SQL.
- Material de Clase: Apuntes y recursos proporcionados durante el ciclo formativo para la estructuración de proyectos y buenas prácticas de programación.
