from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models import RoleEnum, MissionStatusEnum, AlertSeverityEnum
 
# --- Auth ---
 
class UserCreate(BaseModel):
    username: str
    password: str
    role: RoleEnum = RoleEnum.analyst
 
class Token(BaseModel):
    access_token: str
    token_type: str
 
class UserResponse(BaseModel):
    id: int
    username: str
    role: RoleEnum
 
    class Config:
        from_attributes = True

# --- Missions ---

class MissionCreate(BaseModel):
    name: str
    description: str
    destination: str

class MissionResponse(BaseModel):
    id: int
    name: str
    description: str
    destination: str
    status: MissionStatusEnum
    created_at: datetime
    launched_at: Optional[datetime]
    ended_at: Optional[datetime]
 
    class Config:
        from_attributes = True
 
# --- Crew ---
 
class CrewCreate(BaseModel):
    name: str
    role: str
    nationality: str
    experience_missions: int = 0
 
class CrewResponse(BaseModel):
    id: int
    name: str
    role: str
    nationality: str
    experience_missions: int
    mission_id: int
 
    class Config:
        from_attributes = True

# --- Telemetry ---
 
class TelemetryCreate(BaseModel):
    altitude_km: float
    speed_kmh: float
    fuel_percent: float
    oxygen_percent: float
    temperature_c: float
    signal_strength: float
 
class TelemetryResponse(BaseModel):
    id: int
    mission_id: int
    timestamp: datetime
    altitude_km: float
    speed_kmh: float
    fuel_percent: float
    oxygen_percent: float
    temperature_c: float
    signal_strength: float
 
    class Config:
        from_attributes = True
 
# --- Alerts ---
 
class AlertResponse(BaseModel):
    id: int
    mission_id: int
    severity: AlertSeverityEnum
    system: str
    message: str
    resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime]
 
    class Config:
        from_attributes = True
 
# --- Events ---
 
class EventCreate(BaseModel):
    event: str
    details: Optional[str] = None
 
class EventResponse(BaseModel):
    id: int
    mission_id: int
    event: str
    details: Optional[str]
    logged_at: datetime
 
    class Config:
        from_attributes = True
 
# --- Mission Summary ---
 
class MissionSummary(BaseModel):
    mission: MissionResponse
    crew_count: int
    crew: List[CrewResponse]
    total_telemetry_readings: int
    latest_telemetry: Optional[TelemetryResponse]
    total_alerts: int
    unresolved_alerts: int
    critical_alerts: int
    total_events: int
    events: List[EventResponse]

    