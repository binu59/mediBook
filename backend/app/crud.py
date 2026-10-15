from datetime import date, datetime, time

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from . import models, schemas


class SlotTakenError(Exception):
    """The doctor already has an active appointment at that time."""


class AppointmentNotEditableError(Exception):
    """The appointment cannot be edited after it is no longer active."""


class AppointmentNotDeletableError(Exception):
    """The appointment cannot be deleted after it has been completed."""


class AppointmentNotCancellableError(Exception):
    """The appointment cannot be cancelled after it has been completed."""


def _ensure_slot_free(db: Session, doctor: str, when: datetime, status: str, exclude_id: int | None = None):
    if status == schemas.Status.cancelled.value:
        return  # cancelled appointments don't occupy a slot
    stmt = select(models.Appointment.id).where(
        models.Appointment.doctor == doctor,
        models.Appointment.scheduled_at == when,
        models.Appointment.status != schemas.Status.cancelled.value,
    )
    if exclude_id is not None:
        stmt = stmt.where(models.Appointment.id != exclude_id)
    if db.scalars(stmt).first() is not None:
        raise SlotTakenError(f"{doctor} already has an appointment at {when:%Y-%m-%d %H:%M}")


def list_appointments(
    db: Session,
    q: str | None = None,
    status: str | None = None,
    appointment_type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    stmt = select(models.Appointment)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(models.Appointment.patient_name.ilike(like), models.Appointment.doctor.ilike(like)))
    if status:
        stmt = stmt.where(models.Appointment.status == status)
    if appointment_type:
        stmt = stmt.where(models.Appointment.appointment_type == appointment_type)
    if date_from:
        stmt = stmt.where(models.Appointment.scheduled_at >= datetime.combine(date_from, time.min))
    if date_to:
        stmt = stmt.where(models.Appointment.scheduled_at <= datetime.combine(date_to, time.max))
    return db.scalars(stmt.order_by(models.Appointment.id.desc())).all()


def get_appointment(db: Session, appt_id: int):
    return db.get(models.Appointment, appt_id)


def create_appointment(db: Session, data: schemas.AppointmentIn):
    _ensure_slot_free(db, data.doctor, data.scheduled_at, schemas.Status.scheduled.value)
    appt = models.Appointment(**data.model_dump(), status=schemas.Status.scheduled.value)
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


def update_appointment(db: Session, appt: models.Appointment, data: schemas.AppointmentIn):
    if appt.status in (schemas.Status.cancelled.value, schemas.Status.completed.value):
        raise AppointmentNotEditableError(f"{appt.status} appointments cannot be edited")
    _ensure_slot_free(db, data.doctor, data.scheduled_at, appt.status, exclude_id=appt.id)
    for key, value in data.model_dump().items():
        setattr(appt, key, value)
    db.commit()
    db.refresh(appt)
    return appt


def cancel_appointment(db: Session, appt: models.Appointment):
    if appt.status == schemas.Status.completed.value:
        raise AppointmentNotCancellableError("Completed appointments cannot be cancelled")
    if appt.status == schemas.Status.cancelled.value:
        return appt
    appt.status = schemas.Status.cancelled.value
    db.commit()
    db.refresh(appt)
    return appt


def delete_appointment(db: Session, appt: models.Appointment):
    if appt.status == schemas.Status.completed.value:
        raise AppointmentNotDeletableError("Completed appointments cannot be deleted")
    db.delete(appt)
    db.commit()