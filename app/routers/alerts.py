from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.auth import get_current_user, require_commander
from app import models, schemas

router = APIRouter(prefix="/missions", tags=["Alerts"])

@router.get("/{mission_id}/alerts", response_model=List[schemas.AlertResponse])
def get_alerts(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return db.query(models.Alert).filter(
        models.Alert.mission_id == mission_id
    ).order_by(models.Alert.created_at.desc()).all()

@router.get("/{mission_id}/alerts/unresolved", response_model=List[schemas.AlertResponse])
def get_unresolved_alerts(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Alert).filter(
        models.Alert.mission_id == mission_id,
        models.Alert.resolved == False
    ).order_by(models.Alert.created_at.desc()).all()

@router.patch("/{mission_id}/alerts/{alert_id}/resolve", response_model=schemas.AlertResponse)
def resolve_alert(
    mission_id: int,
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    alert = db.query(models.Alert).filter(
        models.Alert.id == alert_id,
        models.Alert.mission_id == mission_id
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.resolved:
        raise HTTPException(status_code=400, detail="Alert already resolved")
    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    event = models.MissionEvent(
        mission_id=mission_id,
        event="Alert Resolved",
        details=f"Alert resolved: {alert.message} by {current_user.username}"
    )
    db.add(event)
    db.commit()
    db.refresh(alert)
    return alert

@router.post("/{mission_id}/alerts/manual", response_model=schemas.AlertResponse)
def create_manual_alert(
    mission_id: int,
    system: str,
    message: str,
    severity: models.AlertSeverityEnum,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_commander)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    alert = models.Alert(
        mission_id=mission_id,
        severity=severity,
        system=system,
        message=message
    )
    db.add(alert)
    event = models.MissionEvent(
        mission_id=mission_id,
        event="Manual Alert Created",
        details=f"[{severity.upper()}] {system}: {message} — by {current_user.username}"
    )
    db.add(event)
    db.commit()
    db.refresh(alert)
    return alert