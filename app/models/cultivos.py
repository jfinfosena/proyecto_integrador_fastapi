from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Cultivos(Base):
    __tablename__ = "cultivos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(100), index=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relación con Usuario
    usuario = relationship(
        "Usuario",
        back_populates="cultivos",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )