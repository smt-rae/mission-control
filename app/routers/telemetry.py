from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth import get_current_user
from app import models, schemas

router = APIRouter(prefix="/missions", tags=["Telemetry"])

# --- Thresholds ---
THRESHOLDS = {
    "fuel_percent":    {"low": 20,   "critical": 10,  "direction": "below"},
    "oxygen_percent":  {"low": 25,   "critical": 15,  "direction": "below"},
    "temperature_c":   {"low": 80,   "critical": 120, "direction": "above"},
    "signal_strength": {"low": 30,   "critical": 15,  "direction": "below"},
}

def check_and_create_alerts(telemetry: models.Telemetry, mission_id: int, db: Session):
    readings = {
        "fuel_percent":    telemetry.fuel_percent,
        "oxygen_percent":  telemetry.oxygen_percent,
        "temperature_c":   telemetry.temperature_c,
        "signal_strength": telemetry.signal_strength,
    }
    labels = {
        "fuel_percent":    "Fuel System",
        "oxygen_percent":  "Life Support",
        "temperature_c":   "Thermal System",
        "signal_strength": "Communications",
    }
    alerts_created = []
    for system, value in readings.items():
        threshold = THRESHOLDS[system]
        direction = threshold["direction"]
        severity = None
        if direction == "below":
            if value <= threshold["critical"]:
                severity = models.AlertSeverityEnum.critical
            elif value <= threshold["low"]:
                severity = models.AlertSeverityEnum.low
        elif direction == "above":
            if value >= threshold["critical"]:
                severity = models.AlertSeverityEnum.critical
            elif value >= threshold["low"]:
                severity = models.AlertSeverityEnum.low
        if severity:
            label = labels[system]
            unit = "%" if "percent" in system else "°C"
            message = (
                f"{label} {'CRITICAL' if severity == models.AlertSeverityEnum.critical else 'WARNING'} — "
                f"{system.replace('_', ' ').title()}: {value}{unit}"
            )
            alert = models.Alert(
                mission_id=mission_id,
                severity=severity,
                system=label,
                message=message
            )
            db.add(alert)
            alerts_created.append(message)
    return alerts_created

@router.post("/{mission_id}/telemetry", response_model=schemas.TelemetryResponse)
def log_telemetry(
    mission_id: int,
    data: schemas.TelemetryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission.status != models.MissionStatusEnum.active:
        raise HTTPException(status_code=400, detail="Telemetry can only be logged for active missions")
    for field, value in data.model_dump().items():
        if field in ["fuel_percent", "oxygen_percent", "signal_strength"] and not (0 <= value <= 100):
            raise HTTPException(status_code=400, detail=f"{field} must be between 0 and 100")
    reading = models.Telemetry(mission_id=mission_id, **data.model_dump())
    db.add(reading)
    db.flush()
    alerts_fired = check_and_create_alerts(reading, mission_id, db)
    db.commit()
    db.refresh(reading)
    response = schemas.TelemetryResponse.model_validate(reading)
    if alerts_fired:
        return {"telemetry": response, "alerts_triggered": alerts_fired}
    return response

@router.get("/{mission_id}/telemetry", response_model=List[schemas.TelemetryResponse])
def get_telemetry(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return db.query(models.Telemetry).filter(
        models.Telemetry.mission_id == mission_id
    ).order_by(models.Telemetry.timestamp.desc()).all()

@router.get("/{mission_id}/telemetry/latest", response_model=schemas.TelemetryResponse)
def get_latest_telemetry(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    reading = db.query(models.Telemetry).filter(
        models.Telemetry.mission_id == mission_id
    ).order_by(models.Telemetry.timestamp.desc()).first()
    if not reading:
        raise HTTPException(status_code=404, detail="No telemetry data yet")
    return reading

@router.get("/{mission_id}/telemetry/averages")
def get_telemetry_averages(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    readings = db.query(models.Telemetry).filter(
        models.Telemetry.mission_id == mission_id
    ).all()
    if not readings:
        raise HTTPException(status_code=404, detail="No telemetry data yet")
    count = len(readings)
    return {
        "total_readings": count,
        "average_altitude_km": round(sum(r.altitude_km for r in readings) / count, 2),
        "average_speed_kmh": round(sum(r.speed_kmh for r in readings) / count, 2),
        "average_fuel_percent": round(sum(r.fuel_percent for r in readings) / count, 2),
        "average_oxygen_percent": round(sum(r.oxygen_percent for r in readings) / count, 2),
        "average_temperature_c": round(sum(r.temperature_c for r in readings) / count, 2),
        "average_signal_strength": round(sum(r.signal_strength for r in readings) / count, 2),
        "min_fuel_recorded": round(min(r.fuel_percent for r in readings), 2),
        "max_temperature_recorded": round(max(r.temperature_c for r in readings), 2),
    }