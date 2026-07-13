from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..auth import crear_access_token, verificar_password
from ..database import get_db
from ..models import Usuario
from ..schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    identificador = payload.nombre.strip()
    if not identificador:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ingresar usuario o email",
        )

    identificador_lower = identificador.lower()
    user = (
        db.query(Usuario)
        .filter(
            or_(
                func.lower(Usuario.nombre) == identificador_lower,
                func.lower(Usuario.email) == identificador_lower,
            )
        )
        .first()
    )

    if not user or not verificar_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o password incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta inactiva",
        )

    token = crear_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        usuario_id=user.id,
        nombre=user.nombre,
    )
