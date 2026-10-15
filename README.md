# MediBook

MediBook is a full-stack appointment booking application. It lets a patient book, view, edit, search, and cancel appointments. Fictional sample data can be loaded for demonstration; no real patient data is included.

**Stack:** FastAPI + SQLAlchemy + SQLite (backend) · React + Vite (frontend) · pytest (backend tests)

## Features

- Book an appointment with a patient name, doctor, date, time, and appointment type.
- Search and filter appointments by patient/doctor, status, type, and date range.
- Edit Scheduled appointments.
- Cancel appointments and reuse the cancelled doctor's time slot.
- Prevent double-booking the same doctor at the same time.
- Display booking confirmation and appointment history views.
- Provide FastAPI interactive documentation at `http://localhost:8000/docs`.

## Run it

Use separate terminals for the backend and frontend.

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.seed                  #load fictional sample data
uvicorn app.main:app --reload      # http://localhost:8000
```

On shells where PowerShell script execution is disabled, activate the environment with:

```bat
.venv\Scripts\activate.bat
```

The SQLite database is created at `backend/appointments.db` when the application starts.

### Frontend

```powershell
cd frontend
npm install
npm run dev                         
```

The Vite development server proxies `/api` requests to `http://localhost:8000`. Start the backend first so those requests succeed.

## Run the tests

```powershell
cd backend
pytest -v
```

The tests use an isolated in-memory SQLite database and do not modify `backend/appointments.db`.

## API

All appointment endpoints use the `/api` prefix. Appointment request bodies contain:

```json
{
  "patient_name": "Test Patient",
  "scheduled_at": "2030-01-10T09:00",
  "doctor": "Dr. A. Example",
  "appointment_type": "Consultation"
}
```

`status` is returned by the API but is not accepted in appointment create/update request bodies. New appointments always start as `Scheduled`.

| Method | Path | Notes |
|---|---|---|
| GET | `/api/appointments` | Lists appointments, newest first. Filters: `q` (patient/doctor), `status`, `appointment_type`, `date_from`, `date_to` |
| POST | `/api/appointments` | Creates a Scheduled appointment; returns `422` for invalid input and `409` if the doctor is double-booked |
| GET | `/api/appointments/{id}` | Gets one appointment; returns `404` when it does not exist |
| PUT | `/api/appointments/{id}` | Edits an active appointment; returns `409` for a cancelled/completed appointment or a conflicting slot |
| POST | `/api/appointments/{id}/cancel` | Cancels an appointment; cancelling an already-cancelled appointment is idempotent |
| DELETE | `/api/appointments/{id}` | Permanently deletes an appointment unless it is Completed |

Allowed status values are `Scheduled`, `Completed`, `Cancelled`, and `No-show`. Allowed appointment types are `Consultation`, `Follow-up`, `Check-up`, and `Procedure`. Invalid or extra request fields are rejected with `422`.

## Project structure

```text
backend/
  app/
    main.py       # FastAPI routes and application lifecycle
    crud.py       # Appointment business rules and database operations
    models.py     # SQLAlchemy database model
    schemas.py    # Pydantic request/response validation
    database.py   # SQLite engine and session dependency
    seed.py       # Optional fictional data loader
  tests/          # Backend API and business-rule tests
frontend/
  src/
    App.jsx             # Main booking/history views
    AppointmentForm.jsx # Booking and edit form
    AppointmentTable.jsx# Appointment cards and actions
    api.js              # API client and error handling
    consants.js         # UI statuses, types, and doctor catalog
```

## Design decisions

- **Status ownership:** New appointments are always Scheduled. Patients can edit or cancel active appointments. Completed appointments cannot be edited, cancelled, or deleted; Completed and No-show are intended for a future staff workflow.
- **Allowed values:** Status and appointment type are validated by the API, not just the UI.
- **Double-booking:** A doctor cannot have two non-cancelled appointments at the same time. Cancelling frees the slot.
- **Doctor selection:** The frontend requires selecting one of its ten catalogued doctors and shows each doctor's specialty. The backend stores the doctor as validated text and does not yet have a `doctors` table.
- **Layered backend:** Routes (`main.py`) call database/business logic (`crud.py`), using models and schemas, so the rules are testable independently of the UI.
- **Server-side filtering:** Filtering is performed by the API, and the UI debounces the search box by 250 ms.
- **Frontend/API boundary:** The frontend currently exposes booking, editing, searching, filtering, and cancellation. The API also supports permanent deletion, but there is no delete button in the current frontend.

## Known limitations / next steps

- No authentication, user accounts, or patient-specific access control.
- The doctor catalog is static in the frontend and is not backed by a database table.
- No pagination or time-zone handling; date-times are stored as entered.
- No production database configuration, migrations, or deployment setup.
- Frontend has no automated tests yet; backend behavior is covered by pytest.