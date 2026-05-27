from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Tramite, Usuario
from ..schemas import CambiarEstadoRequest, ReclamoResponse, ReclamosListResponse

router = APIRouter(prefix="/reclamos", tags=["reclamos"])

RANGOS_FECHA = frozenset({"hoy", "semana", "mes"})


@router.get("", response_model=ReclamosListResponse)
def listar_reclamos(
    estado: str | None = Query(default=None),
    rango: str | None = Query(
        default=None,
        description="Filtro por fecha de creación: hoy, semana (7 días), mes (30 días)",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> ReclamosListResponse:
    if rango is not None and rango not in RANGOS_FECHA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="rango inválido. Valores permitidos: hoy, semana, mes",
        )

    query = db.query(Tramite).filter(Tramite.tipo == "reclamo", Tramite.activo.is_(True))

    if estado is not None:
        query = query.filter(Tramite.estado == estado)

    hoy = date.today()
    if rango == "hoy":
        query = query.filter(Tramite.fecha_creacion == hoy)
    elif rango == "semana":
        query = query.filter(Tramite.fecha_creacion >= hoy - timedelta(days=7))
    elif rango == "mes":
        query = query.filter(Tramite.fecha_creacion >= hoy - timedelta(days=30))

    total = query.count()
    rows = (
        query.order_by(Tramite.fecha_creacion.asc(), Tramite.hora_creacion.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return ReclamosListResponse(
        items=[ReclamoResponse.model_validate(row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch("/{reclamo_id}/estado", response_model=ReclamoResponse)
def cambiar_estado_reclamo(
    reclamo_id: int,
    payload: CambiarEstadoRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> ReclamoResponse:
    reclamo = (
        db.query(Tramite)
        .filter(Tramite.id == reclamo_id, Tramite.tipo == "reclamo", Tramite.activo.is_(True))
        .first()
    )
    if not reclamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reclamo no encontrado",
        )

    nuevo_estado = payload.estado.strip()
    if not nuevo_estado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El estado es obligatorio",
        )

    reclamo.estado = nuevo_estado
    db.commit()
    db.refresh(reclamo)

    return ReclamoResponse.model_validate(reclamo)
