# Backend - Guardia Reclamos

Backend REST minimal con FastAPI para:

- Login JWT con usuarios en MariaDB.
- Listado de reclamos con filtros.
- Cambio de estado de reclamo.

## 1) Requisitos

- Python 3.11+
- MariaDB

## 2) Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 3) Configuracion

Copiar `.env.example` a `.env` y completar credenciales.

## 4) Ejecutar en local

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger:

- [http://localhost:8000/docs](http://localhost:8000/docs)

## 5) Endpoints MVP

- `POST /api/auth/login`
- `GET /api/reclamos`
- `PATCH /api/reclamos/{reclamo_id}/estado`

## 6) Esquema de tablas usado

Este backend usa por defecto estas tablas:

- `usuarios`
  - `id` (PK)
  - `nombre` (UNIQUE)
  - `password_hash` (bcrypt)
  - `activo` (bool)
  - `created_at`
  - `updated_at`

- `tramites`
  - `id` (PK)
  - `nombre`
  - `apellido`
  - `celular`
  - `descripcion`
  - `tipo` (se filtra solo `reclamo`)
  - `estado`
  - `fecha_creacion`
  - `hora_creacion`
  - `activo`

## 7) Requests de ejemplo

Login:

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"admin\",\"password\":\"tu_password\"}"
```

Listar reclamos:

```bash
curl "http://localhost:8000/api/reclamos?estado=pendiente&limit=20&offset=0" \
  -H "Authorization: Bearer TU_TOKEN"
```

Cambiar estado:

```bash
curl -X PATCH "http://localhost:8000/api/reclamos/1/estado" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"estado\":\"realizado\"}"
```
