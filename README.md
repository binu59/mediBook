# MediBook

A small full-stack app to create, view, edit, delete and search appointments.
All sample data is fictional.

**Stack:** FastAPI + SQLAlchemy + SQLite (backend) · React + Vite (frontend) · pytest (tests)

## Run it

```bash
# 1. Backend (http://localhost:8000, API docs at /docs)
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.seed                                   # optional: load fictional sample data
uvicorn app.main:app --reload

# 2. Frontend (new terminal, http://localhost:5173)
cd frontend
npm install
npm run dev
```

## Run the tests
```bash
cd backend && pytest -v
```

## API
| Method | Path | Notes |
|---|---|---|
| GET | `/api/appointments` | Filters: `q` (patient/doctor), `status`, `appointment_type`, `date_from`, `date_to` |
| POST | `/api/appointments` | Creates a Scheduled appointment; 422 invalid, 409 if doctor double-booked |
| GET / PUT | `/api/appointments/{id}` | Read or edit appointment details; status cannot be set by the patient |
| POST | `/api/appointments/{id}/cancel` | Cancels the appointment |

## Design decisions
- **Status ownership:** New appointments are always Scheduled. Patients can cancel appointments, while Completed and No-show are reserved for a future staff workflow.
- **Allowed values:** Status = Scheduled / Completed / Cancelled / No-show; Type = Consultation / Follow-up / Check-up / Procedure. Enforced by the API, not just the UI.
- **Double-booking:** a doctor can't have two non-cancelled appointments at the same time (409). Cancelling frees the slot.
- **Layered backend:** routes (`main.py`) → DB logic (`crud.py`) → models/schemas, so logic is testable without HTTP.
- **Filtering is server-side**; the UI debounces the search box.

## Known limitations / next steps
- No authentication or user accounts.
- Doctors are free text (a `doctors` table would be the next step).
- No pagination, and no time-zone handling (times are stored as entered).
- Frontend has no automated tests yet (backend is covered by pytest).