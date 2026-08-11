from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..models import Dispositivo
from ..schemas import NotificationSendResponse, ReclamoNuevoNotificationRequest
from ..services.expo_push import build_reclamo_message, is_device_not_registered, send_expo_push

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])
settings = get_settings()


def verify_webhook_secret(x_webhook_secret: str | None = Header(default=None)) -> None:
    expected = (settings.webhook_secret or "").strip()
    if not expected or expected == "cambiar_webhook_secret":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="WEBHOOK_SECRET no configurado en el servidor",
        )
    if not x_webhook_secret or x_webhook_secret.strip() != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Webhook secret inválido",
        )


@router.post("/reclamo-nuevo", response_model=NotificationSendResponse)
def notificar_reclamo_nuevo(
    payload: ReclamoNuevoNotificationRequest,
    db: Session = Depends(get_db),
    _: None = Depends(verify_webhook_secret),
) -> NotificationSendResponse:
    if payload.reclamo_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reclamo_id inválido",
        )

    devices = db.query(Dispositivo).filter(Dispositivo.activo.is_(True)).all()
    if not devices:
        return NotificationSendResponse(ok=True, enviados=0, fallidos=0, sin_dispositivos=True)

    messages = [
        build_reclamo_message(
            d.expo_push_token,
            reclamo_id=payload.reclamo_id,
            nombre=payload.nombre,
            apellido=payload.apellido,
            descripcion=payload.descripcion,
        )
        for d in devices
    ]

    try:
        tickets = send_expo_push(messages)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al enviar push a Expo: {exc}",
        ) from exc

    enviados = 0
    fallidos = 0
    for device, ticket in zip(devices, tickets):
        if ticket.get("status") == "ok":
            enviados += 1
            continue
        fallidos += 1
        if is_device_not_registered(ticket):
            device.activo = False

    if fallidos:
        db.commit()

    return NotificationSendResponse(
        ok=True,
        enviados=enviados,
        fallidos=fallidos,
        sin_dispositivos=False,
    )
