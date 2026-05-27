from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import crear_access_token, verificar_password
from ..database import get_db
from ..models import Usuario
from ..schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    username = payload.nombre.strip()
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ingresar nombre de usuario",
        )

    user = db.query(Usuario).filter(func.lower(Usuario.nombre) == func.lower(username)).first()

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
