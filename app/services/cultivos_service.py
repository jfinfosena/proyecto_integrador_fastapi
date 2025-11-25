from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from app.models.cultivos import Cultivos
from app.models.usuario import Usuario
from app.schemas.cultivos import CultivosCreate, CultivosUpdate


def list_cultivos(db: Session, skip: int = 0, limit: int = 100, usuario_id: int | None = None, q: str | None = None) -> list[Cultivos]:
    query = db.query(Cultivos).options(selectinload(Cultivos.usuario))
    if usuario_id is not None:
        query = query.filter(Cultivos.usuario_id == usuario_id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Cultivos.nombre.like(like), Cultivos.tipo.like(like), Cultivos.descripcion.like(like)))
    return query.order_by(Cultivos.id.asc()).offset(skip).limit(limit).all()


def get_cultivo(db: Session, cultivo_id: int) -> Cultivos | None:
    return db.query(Cultivos).options(selectinload(Cultivos.usuario)).filter(Cultivos.id == cultivo_id).first()


def create_cultivo(db: Session, payload: CultivosCreate) -> Cultivos:
    usuario = db.get(Usuario, payload.usuario_id)
    if not usuario:
        raise ValueError("Usuario no existe")
    cultivo = Cultivos(
        nombre=payload.nombre,
        tipo=payload.tipo,
        descripcion=payload.descripcion,
        usuario=usuario
    )
    db.add(cultivo)
    db.commit()
    db.refresh(cultivo)
    return cultivo


def update_cultivo(db: Session, cultivo_id: int, payload: CultivosUpdate) -> Cultivos | None:
    cultivo = get_cultivo(db, cultivo_id)
    if not cultivo:
        return None
    if payload.nombre is not None:
        cultivo.nombre = payload.nombre
    if payload.tipo is not None:
        cultivo.tipo = payload.tipo
    if payload.descripcion is not None:
        cultivo.descripcion = payload.descripcion
    if payload.usuario_id is not None:
        usuario = db.get(Usuario, payload.usuario_id)
        if not usuario:
            raise ValueError("Usuario no existe")
        cultivo.usuario = usuario
    db.add(cultivo)
    db.commit()
    db.refresh(cultivo)
    return cultivo


def delete_cultivo(db: Session, cultivo_id: int) -> bool:
    cultivo = get_cultivo(db, cultivo_id)
    if not cultivo:
        return False
    db.delete(cultivo)
    db.commit()
    return True
