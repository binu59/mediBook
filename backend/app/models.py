from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_name: Mapped[str] = mapped_column(String(100), index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    doctor: Mapped[str] = mapped_column(String(100), index=True)
    appointment_type: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20))