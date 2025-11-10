# 08 - Servicios y lógica de negocio

Los servicios encapsulan la interacción con la base de datos y las reglas de negocio. Mantener esta capa separada de los endpoints facilita el reuso y el mantenimiento.

## Usuarios: `app/services/user_service.py`
```python
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def list_users(db: Session, skip: int = 0, limit: int = 100, search: str | None = None) -> list[User]:
    q = db.query(User)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(User.name.like(like), User.email.like(like)))
    return q.order_by(User.id.asc()).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, payload: UserCreate) -> User:
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise ValueError("Email ya registrado")
    user = User(name=payload.name, email=payload.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, payload: UserUpdate) -> User | None:
    user = get_user(db, user_id)
    if not user:
        return None
    if payload.email and payload.email != user.email:
        if get_user_by_email(db, payload.email):
            raise ValueError("Email ya registrado")
    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        user.email = payload.email
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
```

- Patrón común: `db.add()`, `db.commit()`, `db.refresh()` tras crear/actualizar.
- Validación de unicidad de email con `get_user_by_email`.

## Ítems: `app/services/item_service.py`
```python
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def list_items(db: Session, skip: int = 0, limit: int = 100, owner_id: int | None = None, q: str | None = None) -> list[Item]:
    query = db.query(Item)
    if owner_id is not None:
        query = query.filter(Item.owner_id == owner_id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Item.title.like(like), Item.description.like(like)))
    return query.order_by(Item.id.asc()).offset(skip).limit(limit).all()


def get_item(db: Session, item_id: int) -> Item | None:
    return db.query(Item).filter(Item.id == item_id).first()


def create_item(db: Session, payload: ItemCreate) -> Item:
    item = Item(title=payload.title, description=payload.description, owner_id=payload.owner_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item_id: int, payload: ItemUpdate) -> Item | None:
    item = get_item(db, item_id)
    if not item:
        return None
    if payload.title is not None:
        item.title = payload.title
    if payload.description is not None:
        item.description = payload.description
    if payload.owner_id is not None:
        item.owner_id = payload.owner_id
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item_id: int) -> bool:
    item = get_item(db, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True
```

- Búsquedas con filtros condicionales.
- Actualizaciones parciales respetando `None` para campos no enviados.

## Ventajas de esta capa
- Reutilizable: La lógica queda fuera de los controladores.
- Testeable: Puedes testear servicios sin levantar FastAPI.
- Mantenible: Cambios de negocio no afectan directamente los endpoints.

## Perfiles (1:1): `app/services/profile_service.py`
```python
from sqlalchemy.orm import Session
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate

def list_profiles(db: Session, skip: int = 0, limit: int = 100) -> list[Profile]:
    return db.query(Profile).order_by(Profile.id.asc()).offset(skip).limit(limit).all()

def get_profile(db: Session, profile_id: int) -> Profile | None:
    return db.query(Profile).filter(Profile.id == profile_id).first()

def get_profile_by_user(db: Session, user_id: int) -> Profile | None:
    return db.query(Profile).filter(Profile.user_id == user_id).first()

def create_profile(db: Session, payload: ProfileCreate) -> Profile:
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise ValueError("Usuario no existe")
    if get_profile_by_user(db, payload.user_id):
        raise ValueError("El usuario ya tiene perfil")
    profile = Profile(user_id=payload.user_id, bio=payload.bio, phone=payload.phone, avatar_url=payload.avatar_url)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def update_profile(db: Session, profile_id: int, payload: ProfileUpdate) -> Profile | None:
    profile = get_profile(db, profile_id)
    if not profile:
        return None
    if payload.bio is not None:
        profile.bio = payload.bio
    if payload.phone is not None:
        profile.phone = payload.phone
    if payload.avatar_url is not None:
        profile.avatar_url = payload.avatar_url
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def delete_profile(db: Session, profile_id: int) -> bool:
    profile = get_profile(db, profile_id)
    if not profile:
        return False
    db.delete(profile)
    db.commit()
    return True
```

- Garantiza unicidad 1:1: un usuario solo puede tener un perfil.
- Incluye acceso a `profiles/me` vía el middleware y el token/cookie.

## Categorías (N:N con Ítems): `app/services/category_service.py`

Funciones clave:
- `list_categories(db, skip=0, limit=100, q=None)`: Lista categorías con búsqueda opcional y carga de `items` mediante `selectinload`.
- `get_category(db, category_id)`: Devuelve una categoría por id con sus ítems.
- `get_category_by_name(db, name)`: Recupera por nombre (útil para validaciones únicas).
- `create_category(db, payload: CategoryCreate)`: Crea una categoría.
- `update_category(db, category_id, payload: CategoryUpdate)`: Actualiza `name` y/o `description`.
- `delete_category(db, category_id)`: Elimina la categoría por id.

### Extensiones en Servicio de Ítems: `app/services/item_service.py`

- `list_items(..., category_id=None)`: Filtra ítems por categoría, y hace eager-load de `owner` y `categories`.
- `get_item(db, item_id)`: Carga `owner` y `categories` para respuestas consistentes.
- `create_item(db, payload: ItemCreate)`: Asigna categorías iniciales si se envía `category_ids`.
- `update_item(db, item_id, payload: ItemUpdate)`: Reemplaza categorías si se envía `category_ids` (lista vacía borra todas).

### Esquemas Pydantic relacionados

- `app/schemas/category.py`: `CategoryRead`, `CategoryReadWithItems` (incluye `items` resumidos).
- `app/schemas/item.py`: `ItemCreate`/`ItemUpdate` aceptan `category_ids`; `ItemReadWithOwner` incluye `categories` embebidas.

### Notas de implementación

- Las consultas usan `selectinload` para evitar N+1 y mantener respuestas rápidas.
- El filtro por `category_id` realiza `JOIN` sobre la relación `Item.categories`.
- Se validan existencias de `owner` y categorías al crear/actualizar.