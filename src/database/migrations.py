from src.utils.logger import logger

MIGRATIONS = {
    1: [
        """CREATE TABLE IF NOT EXISTS user_tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )""",
        "CREATE INDEX IF NOT EXISTS idx_filaments_user ON filaments(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_models_user ON models(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)",
        "CREATE INDEX IF NOT EXISTS idx_projects_user_status ON projects(user_id, status)",
        "CREATE INDEX IF NOT EXISTS idx_user_tokens_user ON user_tokens(user_id)",
    ],
    # 2: [...]  # próximas migraciones aquí
}


def run_migrations(db_manager):
    db_manager.execute(
        "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY)"
    )
    current = db_manager.query_one("SELECT MAX(version) as v FROM schema_version")
    current_version = current['v'] if current and current['v'] is not None else 0

    for version, statements in sorted(MIGRATIONS.items()):
        if version > current_version:
            with db_manager.transaction():
                for stmt in statements:
                    db_manager.execute(stmt)
                db_manager.execute(
                    "INSERT INTO schema_version (version) VALUES (?)", (version,)
                )
            logger.info(f"Migración aplicada: v{version}")
