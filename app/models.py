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

    id = Column("ID", Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=True)
    apellido = Column(String(100), nullable=True)
    celular = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    direccion = Column(String(200), nullable=True)
    suministro = Column(String(50), nullable=True)
    tipo = Column(String(20), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    origen = Column(String(20), nullable=False)
    id_conversacion = Column(String(255), nullable=True)
    prioridad = Column(String(20), nullable=True, default="normal")
    estado = Column(String(50), nullable=True, index=True)
    responsable_asignado_id = Column(Integer, nullable=True)
    fecha_creacion = Column(Date, nullable=False, index=True)
    hora_creacion = Column(Time, nullable=False)
    es_anonimo = Column(Boolean, default=False, nullable=True)
    activo = Column(Boolean, default=True, nullable=False, index=True)
