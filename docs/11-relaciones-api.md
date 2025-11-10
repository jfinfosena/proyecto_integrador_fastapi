# 13 - Relaciones de la API y su funcionamiento

Este documento explica las relaciones entre los principales modelos de la API y cómo se gestionan desde los endpoints y servicios.

## Modelos principales

- `User`: representa un usuario del sistema. Relacionado con ítems y perfil.
- `Profile`: información extendida de un usuario (bio, teléfono, avatar). Relación 1:1 con `User`.
- `Item`: recurso creado por usuarios; puede pertenecer a varias categorías. Relación 1:N con `User`.
- `Category`: clasifica ítems. Relación N:N con `Item`.

## Relaciones

### User ⇄ Profile (1:1)

- Cada usuario puede tener un único perfil.
- Endpoints clave:
  - `GET /api/v1/profile`: devuelve datos básicos del usuario autenticado (requiere JWT).
  - `GET /api/v1/profiles/me`: devuelve el perfil completo del usuario autenticado.
  - `POST /api/v1/profiles/`: crea un perfil para un `user_id` (único).
  - `GET/PUT/DELETE /api/v1/profiles/{id}`: CRUD del perfil.
- Servicio: `profile_service.py`
  - Valida existencia del usuario y unicidad de perfil.
  - Permite reasignar el perfil a otro usuario si este no tiene perfil previo.

### User ⇄ Item (1:N)

- Un usuario (owner) puede tener múltiples ítems.
- Endpoints clave:
  - `POST /api/v1/items/`: crea un ítem con `owner_id` obligatorio.
  - `GET /api/v1/items/`: lista ítems; admite filtros por `owner_id` y búsqueda `q`.
  - `GET/PUT/PATCH/DELETE /api/v1/items/{id}`: CRUD del ítem.
- Servicio: `item_service.py`
  - Valida existencia del owner al crear/actualizar.
  - Carga de `owner` mediante `selectinload` para respuestas consistentes.

### Item ⇄ Category (N:N)

- Un ítem puede pertenecer a varias categorías, y una categoría puede incluir varios ítems.
- Endpoints clave:
  - `POST /api/v1/items/` y `PUT/PATCH /api/v1/items/{id}` aceptan `category_ids` para asignar/reemplazar categorías.
  - `GET /api/v1/items?category_id=<id>` filtra ítems por una categoría específica.
  - `GET/POST/PUT/DELETE /api/v1/categories/…` gestiona categorías y expone sus ítems asociados.
- Servicio: `item_service.py` y `category_service.py`
  - `item_service.update_item(..., category_ids=[])` reemplaza por completo la lista de categorías (lista vacía borra todas).
  - `list_items(..., category_id=...)` realiza `JOIN` para filtrar por relación.
  - Se usa `selectinload` para evitar el problema N+1 al serializar relaciones.

## Esquemas y respuestas

- `ItemReadWithOwner`: incluye `owner` y `categories` embebidas.
- `CategoryReadWithItems`: incluye `items` resumidos.
- `ItemCreate/ItemUpdate`: aceptan `category_ids`.
- `UserRead` y `ProfileReadWithUser`: devuelven información de relaciones relevantes.

## Reglas de acceso (resumen)

- `Users`: lectura `admin/user`; escritura `admin` (`POST/PUT/PATCH/DELETE`).
- `Items`: lectura `admin/user/guest`; escritura `admin/user`.
- `Profiles`: lectura y escritura `admin/user`.
- `Categories`: lectura pública si así se configura; por defecto se requiere autenticación.

Adapta estas reglas en `app/core/routes_config.py` según tus necesidades.