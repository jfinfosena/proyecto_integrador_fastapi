# 12 - Scripts de utilidad y pruebas

Este documento describe los scripts disponibles en `scripts/` y cómo utilizarlos para sembrar datos y probar la API completa.

## Scripts disponibles

- `scripts/seed_users.py`
  - Semilla usuarios de prueba (admin, usuarios, invitados) y opcionalmente reinicia la base de datos.
  - Uso:
    - `python scripts/seed_users.py`
    - `python scripts/seed_users.py --reset` reinicia tablas antes de sembrar.

- `scripts/seed_data.py`
  - Semilla un dataset completo: usuarios, perfiles, categorías e ítems asociados.
  - Uso:
    - `python scripts/seed_data.py` siembra datos sin reiniciar el esquema.
    - `python scripts/seed_data.py --reset` elimina y recrea tablas antes de sembrar.
    - `python scripts/seed_data.py --empty` elimina y recrea tablas sin sembrar (útil para pruebas limpias).

- `scripts/test_api.ps1`
  - Script PowerShell para probar la API end-to-end con autenticación, roles y CRUD.
  - Cobertura:
    - Health check y endpoints públicos.
    - Login por email y por nombre de usuario; obtiene JWT.
    - Área admin (requiere rol `admin`).
    - Users: `GET`, `POST`, `GET/{id}`, `PUT`, `PATCH`, `DELETE`.
    - Categories: `GET`, `POST`, `GET/{id}`, `PUT`, `DELETE`.
    - Items: `GET`, `POST` (con `category_ids`), `GET/{id}`, `PUT`, `PATCH` (incluye `category_ids`), `DELETE`.
    - Filtro de ítems por categoría: `GET /api/v1/items?category_id=<id>`.
    - Perfil autenticado: `GET /api/v1/profile` y opcional `GET /api/v1/profiles/me`.
    - Restricciones de invitado: `GET` permitido, `POST` denegado (403) para ítems.

### Parámetros y uso

`test_api.ps1` acepta:

- `-BaseUrl` (por defecto `http://127.0.0.1:8000`) URL base del servicio.
- `-SeedReset` (switch) ejecuta `seed_users.py --reset` antes de las pruebas.
- `-Verbose` (switch) muestra los JSON de petición/respuesta.

Ejemplos:

```powershell
# Ejecutar servidor (ejemplo)
python -m uvicorn app.main:app --reload

# Probar API con salida verbose
pwsh -File scripts/test_api.ps1 -Verbose

# Probar API y reiniciar + sembrar usuarios
pwsh -File scripts/test_api.ps1 -SeedReset

# Usar una URL distinta
pwsh -File scripts/test_api.ps1 -BaseUrl "http://localhost:8000"
```

### Notas

- El script requiere que el servidor FastAPI esté corriendo y accesible.
- Si usas Windows PowerShell clásico, puedes reemplazar `pwsh` por `powershell`.
- Para que `seed_users.py` funcione, asegúrate de tener el entorno virtual activo o un Python con dependencias instaladas.