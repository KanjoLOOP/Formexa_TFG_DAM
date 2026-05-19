# Scripts de mantenimiento

Scripts puntuales usados durante el desarrollo para corregir problemas de schema
históricos en bases de datos de usuarios. **No se ejecutan en producción**.

- `init_db_script.py` — inicialización manual de BD en desarrollo.
- `check_schema.py` / `inspect_db.py` — diagnóstico de estado de BD.
- `clean_triggers.py` / `deep_clean.py` / `inspect_triggers.py` — limpieza de
  triggers residuales por bug histórico de migración.
- `fix_filaments.py` — reparación de FK rota en tabla `filaments`.
