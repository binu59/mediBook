from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Appointment Manager", lifespan=lifespan)


def _get_or_404(db: Session, appt_id: int) -> models.Appointment:
    appt = crud.get_appointment(db, appt_id)
    if appt is None:
        raise HTTPException(404, "Appointment not found")
    return appt


@app.get("/api/appointments", response_model=list[schemas.AppointmentOut])
def list_appointments(
    q: str | None = Query(None, description="Matches patient name or doctor"),
    status: schemas.Status | None = None,
    appointment_type: schemas.AppointmentType | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    return crud.list_appointments(
        db, q, status.value if status else None,
        appointment_type.value if appointment_type else None, date_from, date_to,
    )


@app.post("/api/appointments", response_model=schemas.AppointmentOut, status_code=201)
def create_appointment(data: schemas.AppointmentIn, db: Session = Depends(get_db)):
    try:
        return crud.create_appointment(db, data)
    except crud.SlotTakenError as e:
        raise HTTPException(409, str(e))


@app.get("/api/appointments/{appt_id}", response_model=schemas.AppointmentOut)
def get_appointment(appt_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, appt_id)


@app.put("/api/appointments/{appt_id}", response_model=schemas.AppointmentOut)
def update_appointment(appt_id: int, data: schemas.AppointmentIn, db: Session = Depends(get_db)):
    appt = _get_or_404(db, appt_id)
    try:
        return crud.update_appointment(db, appt, data)
    except crud.AppointmentNotEditableError as e:
        raise HTTPException(409, str(e))
    except crud.SlotTakenError as e:
        raise HTTPException(409, str(e))


@app.post("/api/appointments/{appt_id}/cancel", response_model=schemas.AppointmentOut)
def cancel_appointment(appt_id: int, db: Session = Depends(get_db)):
    try:
        return crud.cancel_appointment(db, _get_or_404(db, appt_id))
    except crud.AppointmentNotCancellableError as e:
        raise HTTPException(409, str(e))


@app.delete("/api/appointments/{appt_id}", status_code=204)
def delete_appointment(appt_id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_appointment(db, _get_or_404(db, appt_id))
    except crud.AppointmentNotDeletableError as e:
        raise HTTPException(409, str(e))
    return Response(status_code=204)