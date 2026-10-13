from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Status(str, Enum):
    scheduled = "Scheduled"
    completed = "Completed"
    cancelled = "Cancelled"
    no_show = "No-show"


class AppointmentType(str, Enum):
    consultation = "Consultation"
    follow_up = "Follow-up"
    check_up = "Check-up"
    procedure = "Procedure"


class AppointmentIn(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    patient_name: str = Field(max_length=100)
    scheduled_at: datetime
    doctor: str = Field(max_length=100)
    appointment_type: AppointmentType
    status: Status = Status.scheduled

    @field_validator("patient_name", "doctor")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v


class AppointmentOut(AppointmentIn):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    id: int