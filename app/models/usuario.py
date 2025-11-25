from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # Hashed password using bcrypt; never store plain passwords
    hashed_password = Column(String(255), nullable=False)
    # Role: 'admin', 'user', or 'guest'
    role = Column(String(20), nullable=False, default="user")

    # Relación uno a muchos con Cultivos
    cultivos = relationship(
        "Cultivos",
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )