import argparse
import sys
from pathlib import Path
from sqlalchemy.orm import Session

# Ensure project root is on sys.path to import 'app.*'
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.database import SessionLocal, Base, engine
from app.schemas.user import UserCreate
from app.schemas.profile import ProfileCreate
from app.schemas.category import CategoryCreate
from app.schemas.item import ItemCreate
from app.services import user_service, profile_service, category_service, item_service


USERS = [
    {"name": "Admin", "email": "admin@example.com", "role": "admin", "password": "admin123"},
    {"name": "Alice", "email": "alice@example.com", "role": "user", "password": "secret"},
    {"name": "Bob", "email": "bob@example.com", "role": "user", "password": "secret"},
    {"name": "Guest", "email": "guest1@example.com", "role": "guest", "password": "guest123"},
]

CATEGORIES = [
    {"name": "Libros", "description": "Material de lectura"},
    {"name": "Novela", "description": "Narrativa"},
    {"name": "Tecnología", "description": "Gadgets y software"},
    {"name": "Cocina", "description": "Recetas y utensilios"},
]


def seed_users_and_profiles(db: Session) -> dict[str, int]:
    ids: dict[str, int] = {}
    for u in USERS:
        existing = user_service.get_user_by_email(db, u["email"])  # type: ignore[attr-defined]
        if existing:
            user_id = existing.id
        else:
            created = user_service.create_user(db, UserCreate(**u))
            user_id = created.id
        ids[u["email"]] = user_id
        # Create profile if missing
        prof = profile_service.get_profile_by_user_id(db, user_id)
        if not prof:
            profile_service.create_profile(db, ProfileCreate(user_id=user_id, bio=f"Perfil de {u['name']}", phone=None, avatar_url=None))
    return ids


def seed_categories(db: Session) -> dict[str, int]:
    ids: dict[str, int] = {}
    for c in CATEGORIES:
        existing = category_service.get_category_by_name(db, c["name"])  # type: ignore[attr-defined]
        if existing:
            cat_id = existing.id
        else:
            created = category_service.create_category(db, CategoryCreate(**c))
            cat_id = created.id
        ids[c["name"]] = cat_id
    return ids


def seed_items(db: Session, user_ids: dict[str, int], category_ids: dict[str, int]):
    admin_id = user_ids.get("admin@example.com")
    alice_id = user_ids.get("alice@example.com")
    bob_id = user_ids.get("bob@example.com")

    libros = category_ids.get("Libros")
    novela = category_ids.get("Novela")
    tecnologia = category_ids.get("Tecnología")
    cocina = category_ids.get("Cocina")

    items_payloads = [
        {"title": "Libro A", "description": "Un libro de ejemplo", "owner_id": admin_id, "category_ids": [libros, novela]},
        {"title": "Laptop Z", "description": "Equipo de tecnología", "owner_id": alice_id, "category_ids": [tecnologia]},
        {"title": "Receta Pasta", "description": "Cocina italiana", "owner_id": bob_id, "category_ids": [cocina]},
        {"title": "Historia C", "description": "Novela histórica", "owner_id": alice_id, "category_ids": [novela, libros]},
    ]

    for p in items_payloads:
        # Limpia None de category_ids si falta alguna categoría
        cats = [cid for cid in (p.get("category_ids") or []) if cid is not None]
        payload = ItemCreate(title=p["title"], description=p["description"], owner_id=p["owner_id"], category_ids=cats)
        item_service.create_item(db, payload)


def main():
    parser = argparse.ArgumentParser(description="Seed full dataset: users, profiles, categories, items")
    parser.add_argument("--reset", action="store_true", help="Drop & recreate tables before seeding")
    parser.add_argument("--empty", action="store_true", help="Drop & recreate tables without seeding")
    args = parser.parse_args()

    if args.reset or args.empty:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    if args.empty:
        print("Schema reset without seeding")
        return

    db = SessionLocal()
    try:
        users = seed_users_and_profiles(db)
        cats = seed_categories(db)
        seed_items(db, users, cats)
        print("Seeding completed:")
        print(f" - Users: {len(users)}")
        print(f" - Categories: {len(cats)}")
        # Count items via service
        items = item_service.list_items(db)
        print(f" - Items: {len(items)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()