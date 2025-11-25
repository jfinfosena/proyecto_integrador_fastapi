from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.schemas.cultivos import CultivosRead, CultivosCreate, CultivosUpdate, CultivosReadWithUsuario
from app.core.database import get_db
from app.services import cultivos_service

router = APIRouter(prefix="/cultivos", tags=["cultivos"])


@router.get("/", response_model=list[CultivosReadWithUsuario])
def list_cultivos(skip: int = 0, limit: int = 100, usuario_id: int | None = None, q: str | None = None, db: Session = Depends(get_db)):
    cultivos = cultivos_service.list_cultivos(db, skip=skip, limit=limit, usuario_id=usuario_id, q=q)
    return cultivos


@router.post("/", response_model=CultivosReadWithUsuario)
def create_cultivo(cultivo: CultivosCreate, db: Session = Depends(get_db)):
    try:
        new_cultivo = cultivos_service.create_cultivo(db, cultivo)
        return new_cultivo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{cultivo_id}", response_model=CultivosReadWithUsuario)
def get_cultivo(cultivo_id: int, db: Session = Depends(get_db)):
    cultivo = cultivos_service.get_cultivo(db, cultivo_id)
    if not cultivo:
        raise HTTPException(status_code=404, detail="Cultivo no encontrado")
    return cultivo


@router.put("/{cultivo_id}", response_model=CultivosReadWithUsuario)
def update_cultivo(cultivo_id: int, payload: CultivosUpdate, db: Session = Depends(get_db)):
    try:
        cultivo = cultivos_service.update_cultivo(db, cultivo_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not cultivo:
        raise HTTPException(status_code=404, detail="Cultivo no encontrado")
    return cultivo


@router.patch("/{cultivo_id}", response_model=CultivosReadWithUsuario)
def patch_cultivo(cultivo_id: int, payload: CultivosUpdate, db: Session = Depends(get_db)):
    try:
        cultivo = cultivos_service.update_cultivo(db, cultivo_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not cultivo:
        raise HTTPException(status_code=404, detail="Cultivo no encontrado")
    return cultivo


@router.delete("/{cultivo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cultivo(cultivo_id: int, db: Session = Depends(get_db)):
    ok = cultivos_service.delete_cultivo(db, cultivo_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cultivo no encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
