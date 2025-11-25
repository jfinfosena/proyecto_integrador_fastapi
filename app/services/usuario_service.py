from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import hash_password


def list_usuarios(db: Session, skip: int = 0, limit: int = 100, search: str | None = None) -> list[Usuario]:
    query = db.query(Usuario).options(selectinload(Usuario.cultivos))
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Usuario.nombre.like(like), Usuario.email.like(like)))
    return query.order_by(Usuario.id.asc()).offset(skip).limit(limit).all()


def get_usuario(db: Session, usuario_id: int) -> Usuario | None:
    return db.query(Usuario).options(selectinload(Usuario.cultivos)).filter(Usuario.id == usuario_id).first()


def get_usuario_by_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()


def create_usuario(db: Session, payload: UsuarioCreate) -> Usuario:
    # Verificar que el email no existe
    existing = get_usuario_by_email(db, payload.email)
    if existing:
        raise ValueError("El email ya está registrado")
    
    usuario = Usuario(
        nombre=payload.nombre,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def update_usuario(db: Session, usuario_id: int, payload: UsuarioUpdate) -> Usuario | None:
    usuario = get_usuario(db, usuario_id)
    if not usuario:
        return None
    
    if payload.nombre is not None:
        usuario.nombre = payload.nombre
    if payload.email is not None:
        # Verificar que el nuevo email no existe (excepto el actual)
        existing = db.query(Usuario).filter(Usuario.email == payload.email, Usuario.id != usuario_id).first()
        if existing:
            raise ValueError("El email ya está registrado")
        usuario.email = payload.email
    if payload.password is not None:
        usuario.hashed_password = hash_password(payload.password)
    if payload.role is not None:
        usuario.role = payload.role
    
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def delete_usuario(db: Session, usuario_id: int) -> bool:
    usuario = get_usuario(db, usuario_id)
    if not usuario:
        return False
    db.delete(usuario)
    db.commit()
    return True
