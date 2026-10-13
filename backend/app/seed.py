"""Load fictional sample data: python -m app.seed"""
from datetime import datetime, timedelta

from . import models
from .database import Base, SessionLocal, engine

PATIENTS = ["Amal Perera", "Nimali Fernando", "Kasun Silva", "Sanduni Jayasuriya", "Ruwan Bandara",
            "Dilini Wickramasinghe", "Tharindu Gunawardena", "Ishara Rajapaksa", "Chamod Senanayake", "Hasini Karunaratne"]
DOCTORS = ["Dr. A. Example", "Dr. B. Sample", "Dr. C. Demo"]
TYPES = ["Consultation", "Follow-up", "Check-up", "Procedure"]
STATUSES = ["Scheduled", "Scheduled", "Completed", "Cancelled", "No-show"]


def seed():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(models.Appointment).count():
            return print("Database already has data; skipping seed.")
        base = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        for i, name in enumerate(PATIENTS):
            db.add(models.Appointment(
                patient_name=name,
                scheduled_at=base + timedelta(days=i - 3, hours=i % 4, minutes=30 * (i % 2)),
                doctor=DOCTORS[i % 3], appointment_type=TYPES[i % 4], status=STATUSES[i % 5]))
        db.commit()
        print(f"Seeded {len(PATIENTS)} fictional appointments.")


if __name__ == "__main__":
    seed()