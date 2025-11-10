# Guías del Proyecto: Project Name API

Bienvenido. Esta documentación te guía paso a paso para entender y trabajar con este proyecto FastAPI + SQLAlchemy, usando Pydantic v2 y una UI de documentación con Scalar.

Índice de tutoriales:
- 01 - Introducción y objetivos: `01-introduccion.md`
- 02 - Instalación y ejecución: `02-instalacion-y-ejecucion.md`
- 03 - Estructura del proyecto: `03-estructura-proyecto.md`
- 04 - Configuración y variables de entorno: `04-configuracion.md`
- 05 - Base de datos y sesiones: `05-base-datos.md`
- 06 - Modelos (SQLAlchemy) y Schemas (Pydantic v2): `06-modelos-y-schemas.md`
- 07 - Rutas y Routers (FastAPI): `07-rutas.md`
- 08 - Servicios y lógica de negocio: `08-servicios.md`
- 09 - Documentación con Scalar: `09-documentacion-scalar.md`
- 10 - Scripts de utilidad y pruebas: `10-scripts.md`
- 11 - Relaciones entre modelos y API: `11-relaciones-api.md`
- 12 - Deploy en Render (Docker): `12-deploy-render.md`

Consejo: Lee en orden, pero si ya puedes ejecutar el servidor, alterna lectura con práctica (probando endpoints).

## Seguridad JWT y Autorización por Roles

Diagrama (simplificado):
```
Client -> /api/v1/login -> Auth Service -> JWT (HS256, exp=60m)
      -> Request -> AuthZ Middleware -> RoutesConfig -> allow/deny -> Endpoint
```

Endpoints clave:
- `POST /api/v1/login`: autentica y devuelve `{ access_token, token_type }`.
- `GET /api/v1/profile`: requiere JWT, devuelve `{ user_id, email, role }`.
- `GET /api/v1/admin`: requiere rol `admin`.
 - Cookie: al iniciar sesión se establece `access_token` (HttpOnly, SameSite=Lax) para uso automático en la documentación `/scalar`.
 - `POST /api/v1/logout`: elimina el cookie para cerrar sesión en el navegador.
 - Perfiles 1:1:
   - `GET /api/v1/profiles/`: lista perfiles.
   - `POST /api/v1/profiles/`: crea perfil para un `user_id` (único).
   - `GET /api/v1/profiles/{id}` | `PUT` | `DELETE`: CRUD de perfil.
   - `GET /api/v1/profiles/me`: devuelve el perfil del usuario autenticado.

Configuración:
- `.env`:
  - `JWT_SECRET="tu_clave_secreta"`
  - `JWT_ALGORITHM="HS256"`
  - `JWT_EXPIRATION_MINUTES=60`
- `app/core/routes_config.py`: control centralizado de acceso por ruta.
- `app/core/auth_middleware.py`: valida JWT y roles por petición.

Ejemplos de login (cURL):
```
# Por email
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Por nombre de usuario (el campo se llama "email" por compatibilidad)
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"Admin","password":"admin123"}'
```

Nota: el endpoint acepta un identificador flexible en el campo `email`. 
Si contiene `@`, se trata como correo; de lo contrario, se busca por nombre.

Ejemplo de acceso protegido:
```
curl "http://localhost:8000/api/v1/profile" -H "Authorization: Bearer <TOKEN>"
```

Uso con cookie (PowerShell):
```
# Mantener sesión y usar el cookie sin copiar el token
$sess = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$body = @{ email = "admin@example.com"; password = "admin123" } | ConvertTo-Json
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/login' -Method Post -ContentType 'application/json' -Body $body -WebSession $sess
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/profile' -Method Get -WebSession $sess
```

Guía de implementación:
1) Modelo `User` ahora incluye `hashed_password` y `role`.
2) Modelo `Profile` con relación 1:1 a `User` (`user_id` único, cascada).
2) Servicio `user_service` hashea contraseñas con `bcrypt`.
3) Servicio `profile_service` garantiza unicidad y CRUD.
3) Utilidades JWT en `app/core/security.py` (HS256, exp=60m).
4) Middleware de autorización en `app/core/auth_middleware.py`.
5) Rutas de autenticación en `app/api/v1/endpoints/auth.py`.
6) Sembrador en `scripts/seed_users.py` con `--reset`.
   - Crea usuarios y sus perfiles por defecto.

Nota: si `CORS_ALLOW_CREDENTIALS=true`, usa orígenes explícitos en `CORS_ALLOW_ORIGINS`.