from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text, Time, func

from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios_app"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Dispositivo(Base):
    __tablename__ = "dispositivos"

    id = Column(Integer, primary_key=True, index=True)
    # Sin ForeignKey en ORM: usuarios_app.id es UNSIGNED y create_all fallaba (errno 150).
    # La FK real se define en SQL (backend/sql/dispositivos.sql).
    usuario_id = Column(Integer, nullable=False, index=True)
    expo_push_token = Column(String(255), nullable=False, unique=True, index=True)
    plataforma = Column(String(20), nullable=False)
    activo = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Tramite(Base):
    __tablename__ = "tramites"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)
    apellido = Column(String(100), nullable=True)
    celular = Column(String(20), nullable=True)
    descripcion = Column(Text, nullable=True)
    direccion = Column(String(200), nullable=True)
    tipo = Column(String(20), nullable=False, index=True)
    estado = Column(String(50), nullable=True, index=True)
    fecha_creacion = Column(Date, nullable=False, index=True)
    hora_creacion = Column(Time, nullable=False)
    activo = Column(Boolean, default=True, nullable=False, index=True)
