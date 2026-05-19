# Mission Control API

A space mission control system built with FastAPI. Commanders can create and manage missions, assign crew, monitor live telemetry, and respond to automated system alerts — all through a fully authenticated REST API.

---

## Features

- **Role based authentication** — Commanders and Analysts have different access levels
- **Mission lifecycle management** — Create, launch, complete, or abort missions
- **Crew assignment** — Assign astronauts with roles and experience levels
- **Live telemetry logging** — Track altitude, speed, fuel, oxygen, temperature, and signal strength
- **Automated alerts** — System automatically fires warnings and critical alerts when readings cross safety thresholds
- **Mission event timeline** — Every action is logged chronologically
- **Mission summary endpoint** — Full mission overview including averages, alert counts, and timeline

---

## Tech Stack

- FastAPI
- SQLAlchemy + SQLite
- Pydantic v2
- JWT Authentication
- Role Based Access Control (RBAC)
- bcrypt password hashing

---

## Project Structure

```
mission-control/
├── main.py
├── requirements.txt
├── app/
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── routers/
│       ├── auth.py
│       ├── missions.py
│       ├── crew.py
│       ├── telemetry.py
│       ├── alerts.py
│       └── events.py
```

---

## Setup

1. Clone the repo

```bash
git clone https://github.com/yourusername/mission-control.git
cd mission-control
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the server

```bash
uvicorn main:app --reload
```

4. Open interactive docs

```
http://127.0.0.1:8000/docs
```

---

## How to Use

### 1. Create accounts

Sign up as a **commander** to create and manage missions, or as an **analyst** to monitor and log data.

### 2. Create a mission (commander only)

POST to `/missions/` with a name, description, and destination.

### 3. Assign crew (commander only)

POST to `/missions/{id}/crew` with crew member details.

### 4. Launch the mission (commander only)

PATCH `/missions/{id}/launch` — requires at least one crew member assigned.

### 5. Log telemetry

POST to `/missions/{id}/telemetry` with live readings. The system automatically checks all values against safety thresholds and fires alerts if anything is out of range.

### 6. Monitor alerts

GET `/missions/{id}/alerts/unresolved` to see active alerts. PATCH `/missions/{id}/alerts/{alert_id}/resolve` to resolve them.

### 7. View the full summary

GET `/missions/{id}/summary` for a complete mission overview.

---

## Automated Alert Thresholds

| System | Warning | Critical |
|---|---|---|
| Fuel | Below 20% | Below 10% |
| Oxygen | Below 25% | Below 15% |
| Temperature | Above 80°C | Above 120°C |
| Signal Strength | Below 30% | Below 15% |

---

## API Endpoints

| Method | Route | Role | Description |
|---|---|---|---|
| POST | /auth/signup | Public | Create account |
| POST | /auth/login | Public | Login, get JWT |
| GET | /auth/me | Any | Current user |
| POST | /missions/ | Commander | Create mission |
| GET | /missions/ | Any | List all missions |
| GET | /missions/active | Any | Active missions only |
| PATCH | /missions/{id}/launch | Commander | Launch mission |
| PATCH | /missions/{id}/complete | Commander | Complete mission |
| PATCH | /missions/{id}/abort | Commander | Abort mission |
| GET | /missions/{id}/summary | Any | Full mission summary |
| POST | /missions/{id}/crew | Commander | Add crew member |
| GET | /missions/{id}/crew | Any | List crew |
| POST | /missions/{id}/telemetry | Any | Log telemetry reading |
| GET | /missions/{id}/telemetry/latest | Any | Latest reading |
| GET | /missions/{id}/telemetry/averages | Any | Telemetry averages |
| GET | /missions/{id}/alerts | Any | All alerts |
| GET | /missions/{id}/alerts/unresolved | Any | Unresolved alerts |
| PATCH | /missions/{id}/alerts/{id}/resolve | Any | Resolve alert |
| GET | /missions/{id}/events | Any | Mission timeline |
| POST | /missions/{id}/events | Any | Log custom event |

---

## What I Learned

- Role based access control with FastAPI dependencies
- Multi-table SQLAlchemy relationships with cascading deletes
- Automated business logic — triggering alerts from telemetry thresholds
- Mission state machine — enforcing valid status transitions
- Aggregating data across related tables for summary endpoints
- Structuring a larger FastAPI project across multiple routers