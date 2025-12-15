# Manual de Usuario - Formexa

## Índice
1. [Instalación](#instalación)
2. [Inicio de Sesión y Registro](#inicio-de-sesión-y-registro)
3. [Módulos](#módulos)
4. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/KanjoLOOP/TFG_DAM.git
   cd Formexa
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicializar la base de datos** (opcional, se hace automáticamente)
   ```bash
   python init_db_script.py
   ```

---

## Inicio de Sesión y Registro

Al abrir la aplicación, verás la pantalla de bienvenida.

### Crear una Cuenta
1. Haz clic en el enlace **"¿No tienes cuenta? Regístrate aquí"**.
2. Introduce un nombre de usuario y una contraseña.
3. Haz clic en **"Registrarse"**.

### Iniciar Sesión
1. Introduce tu nombre de usuario y contraseña.
2. Haz clic en **"Iniciar Sesión"**.

### Modo Invitado
Si solo quieres hacer un cálculo rápido sin guardar datos:
1. Haz clic en **"Continuar como Invitado"**.
2. Tendrás acceso limitado a la **Calculadora de Costes** y la **Configuración**.
3. El resto de funciones (Inventario, Biblioteca, etc.) estarán bloqueadas.

---

## Módulos

### 1. Inicio (Dashboard)
Pantalla principal con un resumen de tu actividad:
- Gráfico de uso de materiales.
- Alertas de stock bajo.
- Accesos directos a funciones recientes.

### 2. Calculadora de Costes

**Objetivo**: Estimar el coste total de una impresión 3D con precisión.

**Cómo usar**:

#### Método Automático (Importar G-code)
1. Haz clic en el botón verde **"Importar G-code (Cura/Prusa)"**.
2. Selecciona un archivo `.gcode` generado por tu slicer (Cura o PrusaSlicer).
3. La aplicación rellenará automáticamente el **Tiempo de Impresión** y el **Peso**.

#### Método Manual
1. Introduce el **peso del modelo** en gramos.
2. Introduce el **tiempo de impresión** (horas y minutos).

#### Configuración de Costes
1. Ajusta el **precio del filamento** (€/kg).
2. Ajusta el **consumo de la impresora** (Watts).
3. Ajusta el **coste de la energía** (€/kWh).
4. Añade **insumos extra** si es necesario (laca, electricidad extra, post-procesado).

#### Resultados y Exportación
1. Haz clic en **"CALCULAR RESULTADOS"**.
2. Verás el desglose de costes y el precio de venta sugerido.
3. Para guardar un informe, haz clic en **"EXPORTAR PDF"**.

---

### 3. Biblioteca de Modelos 3D

**Objetivo**: Organizar y visualizar tus archivos STL.

**Cómo usar**:
1. Haz clic en **"Añadir Modelo"** y selecciona un archivo `.stl`.
2. El modelo se guardará en tu biblioteca.
3. **Haz clic en un modelo** de la lista para verlo en el **Visor 3D** integrado.
4. Puedes rotar y hacer zoom en el modelo para inspeccionarlo.

---

### 4. Inventario de Filamentos

**Objetivo**: Controlar el stock de tus materiales.

**Cómo usar**:
- **Añadir**: Rellena los datos del rollo (Marca, Tipo, Color, Peso, Precio) y pulsa "Añadir".
- **Buscar**: Usa la barra de búsqueda para filtrar por color o material.
- **Eliminar**: Selecciona una fila y pulsa "Eliminar Seleccionado".

---

### 5. Proyectos

**Objetivo**: Gestionar tus trabajos de impresión.
- Crea proyectos para organizar tus impresiones.
- Asigna modelos y materiales a cada proyecto.
- Lleva un seguimiento del estado (Pendiente, En Progreso, Completado).

---

### 6. Marketplace

**Objetivo**: Explorar y descargar modelos 3D (Simulación).
- Navega por el catálogo de modelos disponibles.
- Simula la compra o descarga de diseños de la comunidad.

---

### 7. Configuración

**Objetivo**: Personalizar la aplicación.
- **Idioma**: Cambia entre Español, Inglés y Francés.
- **Sesión**: Cierra sesión o cambia de usuario.
- **Reportar Error**: Envía comentarios sobre problemas encontrados.

---

## Preguntas Frecuentes

### ¿Qué slicers son compatibles con la importación?
Actualmente soportamos archivos G-code generados por **Ultimaker Cura** y **PrusaSlicer** (incluyendo derivados como OrcaSlicer y BambuStudio).

### ¿Dónde se guardan mis datos?
Todos los datos se guardan localmente en un archivo `gestor3d.db` en la carpeta del proyecto.

### ¿Puedo usar la aplicación sin internet?
Sí, es totalmente funcional offline.

### ¿Cómo actualizo el stock de un filamento?
Actualmente es manual, pero estamos trabajando en que se reste automáticamente al confirmar un proyecto.

---

## Soporte
Para reportar errores o sugerencias, abrir un issue en el repositorio de GitHub:
https://github.com/KanjoLOOP/TFG_DAM/issues
