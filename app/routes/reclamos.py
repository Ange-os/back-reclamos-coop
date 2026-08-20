from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Tramite, Usuario
from ..schemas import (
    CambiarEstadoRequest,
    CrearReclamoRequest,
    ReclamoResponse,
    ReclamosListResponse,
)

router = APIRouter(prefix="/reclamos", tags=["reclamos"])

RANGOS_FECHA = frozenset({"hoy", "semana", "mes"})
TIPOS_GUARDIA = frozenset({"reclamo", "emergencia"})
AR_TZ = ZoneInfo("America/Argentina/Buenos_Aires")


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

    query = db.query(Tramite).filter(
        Tramite.tipo.in_(TIPOS_GUARDIA),
        Tramite.activo.is_(True),
    )

    if estado is not None:
        query = query.filter(Tramite.estado == estado)

    hoy = datetime.now(AR_TZ).date()
    if rango == "hoy":
        query = query.filter(Tramite.fecha_creacion == hoy)
    elif rango == "semana":
        query = query.filter(Tramite.fecha_creacion >= hoy - timedelta(days=7))
    elif rango == "mes":
        query = query.filter(Tramite.fecha_creacion >= hoy - timedelta(days=30))

    total = query.count()
    rows = (
        query.order_by(Tramite.fecha_creacion.desc(), Tramite.hora_creacion.desc())
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


@router.post("", response_model=ReclamoResponse, status_code=status.HTTP_201_CREATED)
def crear_reclamo(
    payload: CrearReclamoRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> ReclamoResponse:
    tipo = payload.tipo.strip().lower()
    if tipo not in TIPOS_GUARDIA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tipo inválido. Valores permitidos: reclamo, emergencia",
        )

    descripcion = payload.descripcion.strip()
    if not descripcion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La descripción / problema es obligatoria",
        )

    nombre = payload.nombre.strip()
    if not nombre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre es obligatorio",
        )

    celular = payload.celular.strip() if payload.celular else None
    email = payload.email.strip().lower() if payload.email else None
    if celular == "":
        celular = None
    if email == "":
        email = None

    if not celular and not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debés indicar al menos celular o email",
        )

    direccion = payload.direccion.strip() if payload.direccion else None
    if direccion == "":
        direccion = None

    ahora = datetime.now(AR_TZ)
    tramite = Tramite(
        nombre=nombre,
        apellido=None,
        celular=celular,
        email=email,
        direccion=direccion,
        suministro=None,
        tipo=tipo,
        descripcion=descripcion,
        origen="interno",
        id_conversacion=None,
        prioridad="urgente",
        estado="pendiente",
        responsable_asignado_id=None,
        fecha_creacion=ahora.date(),
        hora_creacion=ahora.time().replace(microsecond=0),
        es_anonimo=False,
        activo=True,
    )
    db.add(tramite)
    db.commit()
    db.refresh(tramite)

    return ReclamoResponse.model_validate(tramite)


@router.patch("/{reclamo_id}/estado", response_model=ReclamoResponse)
def cambiar_estado_reclamo(
    reclamo_id: int,
    payload: CambiarEstadoRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> ReclamoResponse:
    reclamo = (
        db.query(Tramite)
        .filter(
            Tramite.id == reclamo_id,
            Tramite.tipo.in_(TIPOS_GUARDIA),
            Tramite.activo.is_(True),
        )
        .first()
    )
    if not reclamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reclamo o emergencia no encontrado",
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
