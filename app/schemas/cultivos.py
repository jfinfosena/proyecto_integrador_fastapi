from pydantic import BaseModel
from pydantic import ConfigDict


class CultivosBase(BaseModel):
    nombre: str
    tipo: str
    descripcion: str | None = None
    usuario_id: int


class CultivosCreate(CultivosBase):
    pass


class CultivosRead(CultivosBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CultivosUpdate(BaseModel):
    nombre: str | None = None
    tipo: str | None = None
    descripcion: str | None = None
    usuario_id: int | None = None


# Resumen de usuario para embebido en cultivo (evita import circular)
class UsuarioSummary(BaseModel):
    id: int
    nombre: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class CultivosReadWithUsuario(CultivosRead):
    usuario: UsuarioSummary