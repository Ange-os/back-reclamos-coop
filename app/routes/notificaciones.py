from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..schemas import NotificationSendResponse, ReclamoNuevoNotificationRequest
from ..services.expo_push import notify_reclamo_nuevo

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

    try:
        result = notify_reclamo_nuevo(
            db,
            reclamo_id=payload.reclamo_id,
            nombre=payload.nombre,
            apellido=payload.apellido,
            descripcion=payload.descripcion,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al enviar push a Expo: {exc}",
        ) from exc

    return NotificationSendResponse(
        ok=True,
        enviados=int(result["enviados"]),
        fallidos=int(result["fallidos"]),
        sin_dispositivos=bool(result["sin_dispositivos"]),
    )
