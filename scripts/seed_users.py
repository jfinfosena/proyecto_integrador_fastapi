import argparse
import sys
from pathlib import Path
from sqlalchemy.orm import Session
import bcrypt

# Ensure project root is on sys.path to import 'app.*'
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.item import Item
from app.models.usuario import Profile


USERS = [
    {"name": "Admin", "email": "admin@example.com", "role": "admin", "password": "admin123"},
    {"name": "User One", "email": "user1@example.com", "role": "user", "password": "user123"},
    {"name": "User Two", "email": "user2@example.com", "role": "user", "password": "user123"},
    {"name": "User Three", "email": "user3@example.com", "role": "user", "password": "user123"},
    {"name": "Guest One", "email": "guest1@example.com", "role": "guest", "password": "guest123"},
    {"name": "Guest Two", "email": "guest2@example.com", "role": "guest", "password": "guest123"},
]


def reset_data(db: Session):
    db.query(User).delete()
    db.commit()


def seed_users(db: Session):
    for u in USERS:
        hashed = bcrypt.hashpw(u["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user = User(name=u["name"], email=u["email"], role=u["role"], hashed_password=hashed)
        db.add(user)
    db.commit()
    # Crear perfiles para cada usuario
    for u in USERS:
        user = db.query(User).filter(User.email == u["email"]).first()
        if user and not db.query(Profile).filter(Profile.user_id == user.id).first():
            prof = Profile(
                user_id=user.id,
                bio=f"Perfil de {user.name}",
                phone=None,
                avatar_url=None,
            )
            db.add(prof)
    db.commit()


def count_users(db: Session) -> int:
    return db.query(User).count()


def main():
    parser = argparse.ArgumentParser(description="Seed initial users")
    parser.add_argument("--reset", action="store_true", help="Reset test data before seeding")
    parser.add_argument("--empty", action="store_true", help="Drop & recreate tables without seeding")
    args = parser.parse_args()

    # Reset schema if requested (drop and recreate tables to reflect latest models)
    if args.reset or args.empty:
        Base.metadata.drop_all(bind=engine)
    # Ensure tables exist (useful when running the script without starting the API)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if args.empty:
            print("Schema reset without seeding")
            return

        before = count_users(db)
        if args.reset:
            reset_data(db)
        seed_users(db)
        after = count_users(db)
        print(f"Seeding completed (before={before}, after={after})")
    finally:
        db.close()


if __name__ == "__main__":
    main()