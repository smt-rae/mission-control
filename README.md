# Mission Control API

A space mission control system built with FastAPI. Commanders can create and manage missions, assign crew, monitor live telemetry, and respond to automated system alerts — all through a fully authenticated REST API.

🚀 **Live API:** https://web-production-5e22.up.railway.app/docs

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
- SQLAlchemy + PostgreSQL
- Pydantic v2
- JWT Authentication
- Role Based Access Control (RBAC)
- bcrypt password hashing
- Deployed on Railway

---

## Quick Demo

**Everything below is interactive — no setup needed. Just open the live link and follow along.**

👉 Open: https://web-production-5e22.up.railway.app/docs

---

### Step 1 — Create an account

Scroll down to the **Auth** section and click `POST /auth/signup`.

Click **Try it out** in the top right of that panel.

Replace the request body with this and click **Execute**:

```json
{
  "username": "commander1",
  "password": "password123",
  "role": "commander"
}
```

You should get back a 200 response with your user ID. If the username is already taken just pick a different one.

---

### Step 2 — Log in and authorize

Click `POST /auth/login` and click **Try it out**.

Fill in your username and password in the form fields and click **Execute**.

Now scroll all the way back to the top of the page and click the green **Authorize** button. Enter the same username and password and click **Authorize**, then **Close**.

You'll notice the padlock icons next to each endpoint are now closed — that means you're authenticated and every request will include your token automatically.

---

### Step 3 — Create a mission

Scroll to the **Missions** section and click `POST /missions/`.

Click **Try it out** and replace the body with:

```json
{
  "name": "Apollo X",
  "description": "Deep space mission to test new propulsion systems",
  "destination": "Mars"
}
```

Click **Execute**. You'll get back a response like:

```json
{
  "id": 1,
  "name": "Apollo X",
  "status": "planned",
  ...
}
```

**Write down that `id` number — you'll need it for every step below.**

---

### Step 4 — Assign crew

Scroll to the **Crew** section and click `POST /missions/{mission_id}/crew`.

Click **Try it out**, enter your mission ID in the `mission_id` field, and use this body:

```json
{
  "name": "Neil Armstrong",
  "role": "Commander",
  "nationality": "American",
  "experience_missions": 2
}
```

Click **Execute**. Add a second crew member if you want.

---

### Step 5 — Launch the mission

Find `PATCH /missions/{mission_id}/launch` in the Missions section.

Click **Try it out**, enter your mission ID, and click **Execute**.

The mission status will change from `planned` to `active`. You cannot launch without crew — the system will block it.

---

### Step 6 — Log telemetry and trigger an alert

This is where it gets interesting. Find `POST /missions/{mission_id}/telemetry` in the **Telemetry** section.

Click **Try it out**, enter your mission ID, and use this body — notice the critically low fuel and oxygen:

```json
{
  "altitude_km": 408.5,
  "speed_kmh": 27600,
  "fuel_percent": 5,
  "oxygen_percent": 10,
  "temperature_c": 95,
  "signal_strength": 87
}
```

Click **Execute**. The system will automatically detect the dangerous readings and fire critical alerts without any manual input.

---

### Step 7 — View the alerts

Find `GET /missions/{mission_id}/alerts/unresolved` in the **Alerts** section.

Enter your mission ID and click **Execute**. You'll see the critical alerts the system automatically created from your telemetry reading.

---

### Step 8 — Resolve an alert

Find `PATCH /missions/{mission_id}/alerts/{alert_id}/resolve`.

Enter your mission ID and the alert ID from the previous step. Click **Execute** to mark it resolved.

---

### Step 9 — View the full mission summary

Find `GET /missions/{mission_id}/summary` in the Missions section.

Enter your mission ID and click **Execute**.

You'll get back a complete picture of the mission — crew list, total telemetry readings, average fuel and temperature, alert counts, and a full chronological event timeline showing every action taken from mission creation to now.

---

## Automated Alert Thresholds

| System | Warning | Critical |
|---|---|---|
| Fuel | Below 20% | Below 10% |
| Oxygen | Below 25% | Below 15% |
| Temperature | Above 80°C | Above 120°C |
| Signal Strength | Below 30% | Below 15% |

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

## Local Setup

1. Clone the repo

```bash
git clone https://github.com/smt-rae/mission-control.git
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
- Deploying a FastAPI app with PostgreSQL on Railway