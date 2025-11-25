from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict


class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    password: str
    role: str = "user"


class UsuarioRead(UsuarioBase):
    id: int
    role: str
    model_config = ConfigDict(from_attributes=True)


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: str | None = None


# Resumen de cultivo para embebido en usuario (evita import circular)
class CultivoSummary(BaseModel):
    id: int
    nombre: str
    tipo: str
    descripcion: str | None = None
    usuario_id: int
    model_config = ConfigDict(from_attributes=True)


class UsuarioReadWithCultivos(UsuarioRead):
    cultivos: list[CultivoSummary] = []
