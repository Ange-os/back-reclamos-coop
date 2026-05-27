from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    nombre: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario_id: int
    nombre: str


class ReclamoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    celular: Optional[str] = None
    descripcion: Optional[str] = None
    direccion: Optional[str] = None
    estado: Optional[str] = None
    fecha_creacion: date


class ReclamosListResponse(BaseModel):
    items: list[ReclamoResponse]
    total: int
    limit: int
    offset: int


class CambiarEstadoRequest(BaseModel):
    estado: str
