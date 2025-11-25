from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.schemas.usuario import UsuarioReadWithCultivos, UsuarioCreate, UsuarioUpdate
from app.core.database import get_db
from app.services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/", response_model=list[UsuarioReadWithCultivos])
def list_usuarios(skip: int = 0, limit: int = 100, search: str | None = None, db: Session = Depends(get_db)):
    usuarios = usuario_service.list_usuarios(db, skip=skip, limit=limit, search=search)
    return usuarios


@router.post("/", response_model=UsuarioReadWithCultivos)
def create_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        new_usuario = usuario_service.create_usuario(db, usuario)
        return new_usuario
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{usuario_id}", response_model=UsuarioReadWithCultivos)
def get_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = usuario_service.get_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioReadWithCultivos)
def update_usuario(usuario_id: int, payload: UsuarioUpdate, db: Session = Depends(get_db)):
    try:
        usuario = usuario_service.update_usuario(db, usuario_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.patch("/{usuario_id}", response_model=UsuarioReadWithCultivos)
def patch_usuario(usuario_id: int, payload: UsuarioUpdate, db: Session = Depends(get_db)):
    try:
        usuario = usuario_service.update_usuario(db, usuario_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):
    ok = usuario_service.delete_usuario(db, usuario_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
