from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, missions, crew, telemetry, alerts, events

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mission Control API",
    description="A space mission control system for managing missions, crew, telemetry, and alerts.",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(missions.router)
app.include_router(crew.router)
app.include_router(telemetry.router)
app.include_router(alerts.router)
app.include_router(events.router)

@app.get("/")
def root():
    return {
        "message": "Mission Control API is online.",
        "docs": "/docs",
        "status": "All systems nominal"
    }