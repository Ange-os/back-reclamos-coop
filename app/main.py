from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes import auth, devices, notificaciones, reclamos


app = FastAPI(
    title="Guardia Reclamos API",
    version="0.2.0",
    description="API REST para login, reclamos y notificaciones push.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas faltantes sin tumbar el servicio si alguna FK ya existe / falla.
try:
    Base.metadata.create_all(bind=engine)
except Exception as exc:
    # En producción las tablas se crean por SQL; no debe impedir el arranque.
    print(f"[WARN] create_all omitido/falló: {exc}")

app.include_router(auth.router, prefix="/api")
app.include_router(reclamos.router, prefix="/api")
app.include_router(devices.router, prefix="/api")
app.include_router(notificaciones.router, prefix="/api")


@app.get("/")
def root() -> dict:
    return {"status": "ok", "service": "guardia-reclamos-api"}


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}
