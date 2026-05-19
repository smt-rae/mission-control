from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth import get_current_user, require_commander
from app import models, schemas

router = APIRouter(prefix="/missions", tags=["Crew"])

@router.post("/{mission_id}/crew", response_model=schemas.CrewResponse)
def add_crew(
    mission_id: int,
    data: schemas.CrewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_commander)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission.status == models.MissionStatusEnum.active:
        raise HTTPException(status_code=400, detail="Cannot add crew to an active mission")
    member = models.CrewMember(
        name=data.name,
        role=data.role,
        nationality=data.nationality,
        experience_missions=data.experience_missions,
        mission_id=mission_id
    )
    db.add(member)
    event = models.MissionEvent(
        mission_id=mission_id,
        event="Crew Member Assigned",
        details=f"{data.name} ({data.role}) assigned to mission"
    )
    db.add(event)
    db.commit()
    db.refresh(member)
    return member

@router.get("/{mission_id}/crew", response_model=List[schemas.CrewResponse])
def get_crew(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission.crew

@router.delete("/{mission_id}/crew/{crew_id}")
def remove_crew(
    mission_id: int,
    crew_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_commander)
):
    member = db.query(models.CrewMember).filter(
        models.CrewMember.id == crew_id,
        models.CrewMember.mission_id == mission_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Crew member not found")
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if mission.status == models.MissionStatusEnum.active:
        raise HTTPException(status_code=400, detail="Cannot remove crew from active mission")
    name = member.name
    db.delete(member)
    event = models.MissionEvent(
        mission_id=mission_id,
        event="Crew Member Removed",
        details=f"{name} removed from mission"
    )
    db.add(event)
    db.commit()
    return {"message": f"{name} removed from mission"}