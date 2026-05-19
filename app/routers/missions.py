from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.auth import get_current_user, require_commander
from app import models, schemas

router = APIRouter(prefix="/missions", tags=["Missions"])

@router.post("/", response_model=schemas.MissionResponse)
def create_mission(
    data: schemas.MissionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_commander)
):
    mission = models.Mission(
        name=data.name,
        description=data.description,
        destination=data.destination,
        created_by_id=current_user.id
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)
    event = models.MissionEvent(
        mission_id=mission.id,
        event="Mission Created",
        details=f"Mission '{mission.name}' created by {current_user.username}"
    )
    db.add(event)
    db.commit()
    return mission

@router.get("/", response_model=List[schemas.MissionResponse])
def get_all_missions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Mission).all()

@router.get("/active", response_model=List[schemas.MissionResponse])
def get_active_missions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Mission).filter(
        models.Mission.status == models.MissionStatusEnum.active
    ).all()

@router.get("/{mission_id}", response_model=schemas.MissionResponse)
def get_mission(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

@router.patch("/{mission_id}/launch", response_model=schemas.MissionResponse)
def launch_mission(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_commander)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission.status != models.MissionStatusEnum.planned:
        raise HTTPException(status_code=400, detail=f"Cannot launch a mission with status '{mission.status}'")
    crew_count = len(mission.crew)
    if crew_count == 0:
        raise HTTPException(status_code=400, detail="Cannot launch — no crew assigned")
    mission.status = models.MissionStatusEnum.active
    mission.launched_at = datetime.utcnow()
    event = models.MissionEvent(
        mission_id=mission.id,
        event="Mission Launched",
        details=f"Launch confirmed by {current_user.username}. Crew: {crew_count}"
    )
    db.add(event)
    db.commit()
    db.refresh(mission)
    return mission

@router.patch("/{mission_id}/complete", response_model=schemas.MissionResponse)
def complete_mission(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_commander)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission.status != models.MissionStatusEnum.active:
        raise HTTPException(status_code=400, detail="Only active missions can be completed")
    mission.status = models.MissionStatusEnum.completed
    mission.ended_at = datetime.utcnow()
    event = models.MissionEvent(
        mission_id=mission.id,
        event="Mission Completed",
        details=f"Mission completed successfully by {current_user.username}"
    )
    db.add(event)
    db.commit()
    db.refresh(mission)
    return mission

@router.patch("/{mission_id}/abort", response_model=schemas.MissionResponse)
def abort_mission(
    mission_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_commander)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission.status not in [models.MissionStatusEnum.planned, models.MissionStatusEnum.active]:
        raise HTTPException(status_code=400, detail="Mission cannot be aborted")
    mission.status = models.MissionStatusEnum.aborted
    mission.ended_at = datetime.utcnow()
    alert = models.Alert(
        mission_id=mission.id,
        severity=models.AlertSeverityEnum.critical,
        system="Mission Control",
        message=f"MISSION ABORTED — {reason}"
    )
    event = models.MissionEvent(
        mission_id=mission.id,
        event="Mission Aborted",
        details=f"Aborted by {current_user.username}. Reason: {reason}"
    )
    db.add(alert)
    db.add(event)
    db.commit()
    db.refresh(mission)
    return mission

@router.get("/{mission_id}/summary")
def get_mission_summary(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    telemetry = db.query(models.Telemetry).filter(
        models.Telemetry.mission_id == mission_id
    ).order_by(models.Telemetry.timestamp.desc()).all()
    alerts = db.query(models.Alert).filter(models.Alert.mission_id == mission_id).all()
    events = db.query(models.MissionEvent).filter(
        models.MissionEvent.mission_id == mission_id
    ).order_by(models.MissionEvent.logged_at.asc()).all()
    unresolved = sum(1 for a in alerts if not a.resolved)
    critical = sum(1 for a in alerts if a.severity == models.AlertSeverityEnum.critical)
    avg_fuel = round(sum(t.fuel_percent for t in telemetry) / len(telemetry), 2) if telemetry else None
    avg_temp = round(sum(t.temperature_c for t in telemetry) / len(telemetry), 2) if telemetry else None
    return {
        "mission": mission,
        "crew_count": len(mission.crew),
        "crew": mission.crew,
        "telemetry_readings": len(telemetry),
        "latest_telemetry": telemetry[0] if telemetry else None,
        "average_fuel_percent": avg_fuel,
        "average_temperature_c": avg_temp,
        "total_alerts": len(alerts),
        "unresolved_alerts": unresolved,
        "critical_alerts": critical,
        "total_events": len(events),
        "timeline": events
    }

@router.delete("/{mission_id}")
def delete_mission(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_commander)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission.status == models.MissionStatusEnum.active:
        raise HTTPException(status_code=400, detail="Cannot delete an active mission — abort first")
    db.delete(mission)
    db.commit()
    return {"message": f"Mission '{mission.name}' deleted"}