"""Envío de notificaciones push vía Expo Push API."""

from __future__ import annotations

from typing import Any

import httpx
from sqlalchemy.orm import Session

from ..models import Dispositivo

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


def build_reclamo_message(
    token: str,
    *,
    reclamo_id: int,
    nombre: str | None,
    apellido: str | None,
    descripcion: str | None,
) -> dict[str, Any]:
    persona = " ".join(part for part in [nombre or "", apellido or ""] if part).strip() or "Sin nombre"
    detalle = (descripcion or "Nuevo reclamo").strip()
    if len(detalle) > 80:
        detalle = detalle[:77] + "..."

    return {
        "to": token,
        "sound": "default",
        "title": f"Nuevo reclamo #{reclamo_id}",
        "body": f"{persona} — {detalle}",
        "data": {"reclamoId": reclamo_id, "tipo": "reclamo_nuevo"},
        "priority": "high",
        "channelId": "reclamos",
    }


def send_expo_push(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Envía mensajes a Expo. Devuelve la lista `data` de tickets."""
    if not messages:
        return []

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            EXPO_PUSH_URL,
            json=messages,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        payload = response.json()

    data = payload.get("data", [])
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    return []


def is_device_not_registered(ticket: dict[str, Any]) -> bool:
    if ticket.get("status") != "error":
        return False
    details = ticket.get("details") or {}
    error = details.get("error") if isinstance(details, dict) else None
    return error == "DeviceNotRegistered"


def notify_reclamo_nuevo(
    db: Session,
    *,
    reclamo_id: int,
    nombre: str | None = None,
    apellido: str | None = None,
    descripcion: str | None = None,
) -> dict[str, Any]:
    """
    Envía push a todos los dispositivos activos.
    Desactiva tokens con DeviceNotRegistered.
    """
    devices = db.query(Dispositivo).filter(Dispositivo.activo.is_(True)).all()
    if not devices:
        return {"enviados": 0, "fallidos": 0, "sin_dispositivos": True}

    messages = [
        build_reclamo_message(
            d.expo_push_token,
            reclamo_id=reclamo_id,
            nombre=nombre,
            apellido=apellido,
            descripcion=descripcion,
        )
        for d in devices
    ]

    tickets = send_expo_push(messages)

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

    return {
        "enviados": enviados,
        "fallidos": fallidos,
        "sin_dispositivos": False,
    }
