# 10 - Documentación con Scalar

Este proyecto usa `scalar-fastapi` para renderizar una UI moderna sobre el documento OpenAPI que genera FastAPI.

## Ruta de Scalar

`app/main.py` incluye:
```python
from scalar_fastapi import get_scalar_api_reference

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        scalar_proxy_url="https://proxy.scalar.com",
    )
```

Claves:
- `include_in_schema=False` evita que `/scalar` aparezca en el OpenAPI.
- `openapi_url=app.openapi_url` hace que Scalar consuma el OpenAPI generado por FastAPI.
- `scalar_proxy_url` ayuda con CORS cuando abres la UI en entornos que requieren proxy.

## ¿Por qué no veo todos los endpoints?

Revisa estos puntos:
1. Asegúrate de que `app` sea único y el mismo que registra routers. Evita doble inicialización.
   - En `main.py` debe haber una sola instancia `app = FastAPI(...)` y la línea `app.include_router(api_router)`.
2. Verifica que los endpoints estén correctamente incluidos en `api_router`:
   - `api/v1/routers.py` debe incluir `users.router` e `items.router`.
3. Asegúrate de no usar `include_in_schema=False` en endpoints que quieres documentar.
4. Revisa prefijos y tags:
   - `APIRouter(prefix="/users", tags=["users"])` bajo `APIRouter(prefix="/api/v1")` → rutas tipo `/api/v1/users/...`.
5. Si cambiaste la URL base del OpenAPI, asegúrate de que `openapi_url` sea accesible.

## Acceder a la UI de Scalar

- Levanta el servidor: `uvicorn app.main:app --reload`.
- Abre: `http://127.0.0.1:8000/scalar`.
- Interactúa con las rutas desde la UI.

### Autenticación en Scalar sin copiar token
- Realiza `POST /api/v1/login` desde la UI; el servidor establecerá un cookie `access_token` (HttpOnly) con el JWT.
- A partir de ahí, las solicitudes desde la UI se enviarán autenticadas automáticamente usando ese cookie.
- Para cerrar sesión del navegador, usa `POST /api/v1/logout` (borra el cookie).

## Personalización básica
- Cambia el `title` en `FastAPI(title=settings.app_name)` para que tu API tenga nombre en la UI.
- Usa `tags` en routers para agrupar endpoints.

## Diferencias con SwaggerUI
- Scalar ofrece una UI alternativa moderna.
- Ambos leen el mismo documento OpenAPI; si la UI no muestra algo, el problema suele estar en la configuración o en el registro de rutas.