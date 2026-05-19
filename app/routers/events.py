from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth import get_current_user
from app import models, schemas

router = APIRouter(prefix="/missions", tags=["Events"])

@router.get("/{mission_id}/events", response_model=List[schemas.EventResponse])
def get_events(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return db.query(models.MissionEvent).filter(
        models.MissionEvent.mission_id == mission_id
    ).order_by(models.MissionEvent.logged_at.asc()).all()

@router.post("/{mission_id}/events", response_model=schemas.EventResponse)
def log_event(
    mission_id: int,
    data: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    event = models.MissionEvent(
        mission_id=mission_id,
        event=data.event,
        details=data.details
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event