-- Script de creación de base de datos para Gestor 3D (SQLite)

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email TEXT,
    is_guest INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Tabla de Materiales (Filamentos)
CREATE TABLE IF NOT EXISTS filaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    material_type TEXT NOT NULL, -- PLA, PETG, ABS, etc.
    color TEXT NOT NULL,
    diameter REAL DEFAULT 1.75, -- mm
    density REAL DEFAULT 1.24, -- g/cm3
    weight_initial REAL NOT NULL, -- gramos (e.g., 1000g)
    weight_current REAL NOT NULL, -- gramos
    price REAL NOT NULL, -- Coste del rollo
    purchase_date DATE,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Tabla de Modelos 3D (Biblioteca)
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    file_path TEXT NOT NULL, -- Ruta al archivo STL local
    thumbnail_path TEXT, -- Ruta a la imagen generada
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de Proyectos
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'Planificado', -- SQLite no tiene ENUM nativo, se maneja como TEXT
    start_date DATETIME,
    end_date DATETIME,
    total_cost REAL DEFAULT 0.00,
    print_time_minutes INTEGER DEFAULT 0,
    energy_cost REAL DEFAULT 0.00,
    filament_cost REAL DEFAULT 0.00,
    model_id INTEGER,
    filament_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL,
    FOREIGN KEY (filament_id) REFERENCES filaments(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
