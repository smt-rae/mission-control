from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class RoleEnum(str, enum.Enum):
    commander = "commander"
    analyst = "analyst"

class MissionStatusEnum(str, enum.Enum):
    planned = "planned"
    active = "active"
    completed = "completed"
    aborted = "aborted"

class AlertSeverityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    critical = "critical"

# --- Users ---

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.analyst)
    missions = relationship("Mission", back_populates="created_by")

# --- Missions ---

class Mission(Base):
    __tablename__ = "missions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    destination = Column(String)
    status = Column(Enum(MissionStatusEnum), default=MissionStatusEnum.planned)
    created_at = Column(DateTime, default=datetime.utcnow)
    launched_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("User", back_populates="missions")
    crew = relationship("CrewMember", back_populates="mission", cascade="all, delete")
    telemetry = relationship("Telemetry", back_populates="mission", cascade="all, delete")
    alerts = relationship("Alert", back_populates="mission", cascade="all, delete")
    events = relationship("MissionEvent", back_populates="mission", cascade="all, delete")

# --- Crew ---

class CrewMember(Base):
    __tablename__ = "crew"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    nationality = Column(String)
    experience_missions = Column(Integer, default=0)
    mission_id = Column(Integer, ForeignKey("missions.id"))
    mission = relationship("Mission", back_populates="crew")

# --- Telemetry ---

class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    altitude_km = Column(Float)
    speed_kmh = Column(Float)
    fuel_percent = Column(Float)
    oxygen_percent = Column(Float)
    temperature_c = Column(Float)
    signal_strength = Column(Float)
    mission = relationship("Mission", back_populates="telemetry")

# --- Alerts ---

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"))
    severity = Column(Enum(AlertSeverityEnum))
    system = Column(String)
    message = Column(String)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    mission = relationship("Mission", back_populates="alerts")

# --- Mission Events ---

class MissionEvent(Base):
    __tablename__ = "mission_events"
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"))
    event = Column(String)
    details = Column(String, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow)
    mission = relationship("Mission", back_populates="events")

    