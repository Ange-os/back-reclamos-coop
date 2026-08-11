from datetime import date, time
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
    hora_creacion: time


class ReclamosListResponse(BaseModel):
    items: list[ReclamoResponse]
    total: int
    limit: int
    offset: int


class CambiarEstadoRequest(BaseModel):
    estado: str


class DeviceRegisterRequest(BaseModel):
    expo_push_token: str
    plataforma: str  # android | ios


class DeviceResponse(BaseModel):
    ok: bool = True
    mensaje: str = "Dispositivo registrado"


class ReclamoNuevoNotificationRequest(BaseModel):
    reclamo_id: int
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    descripcion: Optional[str] = None
    celular: Optional[str] = None


class NotificationSendResponse(BaseModel):
    ok: bool = True
    enviados: int = 0
    fallidos: int = 0
    sin_dispositivos: bool = False
