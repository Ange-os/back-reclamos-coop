from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Dispositivo, Usuario
from ..schemas import DeviceRegisterRequest, DeviceResponse

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("", response_model=DeviceResponse)
def register_device(
    payload: DeviceRegisterRequest,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> DeviceResponse:
    token = payload.expo_push_token.strip()
    plataforma = payload.plataforma.strip().lower()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expo_push_token es obligatorio",
        )
    if plataforma not in {"android", "ios"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="plataforma debe ser android o ios",
        )

    existing = db.query(Dispositivo).filter(Dispositivo.expo_push_token == token).first()
    if existing:
        existing.usuario_id = user.id
        existing.plataforma = plataforma
        existing.activo = True
        db.commit()
        return DeviceResponse(mensaje="Dispositivo actualizado")

    device = Dispositivo(
        usuario_id=user.id,
        expo_push_token=token,
        plataforma=plataforma,
        activo=True,
    )
    db.add(device)
    db.commit()
    return DeviceResponse(mensaje="Dispositivo registrado")


@router.delete("", response_model=DeviceResponse)
def unregister_device(
    payload: DeviceRegisterRequest,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> DeviceResponse:
    token = payload.expo_push_token.strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expo_push_token es obligatorio",
        )

    device = (
        db.query(Dispositivo)
        .filter(
            Dispositivo.expo_push_token == token,
            Dispositivo.usuario_id == user.id,
        )
        .first()
    )
    if device:
        device.activo = False
        db.commit()

    return DeviceResponse(mensaje="Dispositivo desactivado")
