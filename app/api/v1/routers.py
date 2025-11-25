from fastapi import APIRouter
from .endpoints import cultivos, usuario

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(cultivos.router)
api_router.include_router(usuario.router)