from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes import auth, reclamos


app = FastAPI(
    title="Guardia Reclamos API",
    version="0.1.0",
    description="API REST para login y gestion de reclamos.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crea tablas si no existen. Luego podes migrar a Alembic.
Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api")
app.include_router(reclamos.router, prefix="/api")


@app.get("/")
def root() -> dict:
    return {"status": "ok", "service": "guardia-reclamos-api"}


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}
