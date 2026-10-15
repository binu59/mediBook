import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    def override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def payload(**overrides):
    base = {"patient_name": "Test Patient", "scheduled_at": "2030-01-10T09:00", "doctor": "Dr. Demo",
            "appointment_type": "Consultation"}
    return {**base, **overrides}


def test_create_and_get(client):
    r = client.post("/api/appointments", json=payload())
    assert r.status_code == 201
    created = r.json()
    assert client.get(f"/api/appointments/{created['id']}").json()["patient_name"] == "Test Patient"


def test_list_newest_appointments_first(client):
    first = client.post("/api/appointments", json=payload(scheduled_at="2030-01-11T09:00")).json()
    second = client.post("/api/appointments", json=payload(scheduled_at="2030-01-10T09:00")).json()

    appointments = client.get("/api/appointments").json()

    assert [a["id"] for a in appointments] == [second["id"], first["id"]]


def test_update(client):
    appt_id = client.post("/api/appointments", json=payload()).json()["id"]
    r = client.put(f"/api/appointments/{appt_id}", json=payload(patient_name="Updated Patient"))
    assert r.status_code == 200
    assert r.json()["patient_name"] == "Updated Patient"
    assert r.json()["status"] == "Scheduled"


def test_delete(client):
    appt_id = client.post("/api/appointments", json=payload()).json()["id"]
    assert client.delete(f"/api/appointments/{appt_id}").status_code == 204
    assert client.get(f"/api/appointments/{appt_id}").status_code == 404


def test_not_found(client):
    assert client.put("/api/appointments/999", json=payload()).status_code == 404
    assert client.delete("/api/appointments/999").status_code == 404


@pytest.mark.parametrize("bad", [
    {"patient_name": "   "}, {"doctor": ""}, {"status": "Maybe"},
    {"appointment_type": "Surgery"}, {"scheduled_at": "not-a-date"},
])
def test_validation_rejects_bad_input(client, bad):
    assert client.post("/api/appointments", json=payload(**bad)).status_code == 422


def test_new_appointment_always_starts_scheduled(client):
    response = client.post("/api/appointments", json=payload(status="Cancelled"))
    assert response.status_code == 422
    created = client.post("/api/appointments", json=payload()).json()
    assert created["status"] == "Scheduled"


def test_cancel_appointment(client):
    appt_id = client.post("/api/appointments", json=payload()).json()["id"]
    response = client.post(f"/api/appointments/{appt_id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "Cancelled"
    assert client.post(f"/api/appointments/{appt_id}/cancel").json()["status"] == "Cancelled"


def test_cancelled_appointment_cannot_be_updated(client):
    appt_id = client.post("/api/appointments", json=payload()).json()["id"]
    client.post(f"/api/appointments/{appt_id}/cancel")

    response = client.put(f"/api/appointments/{appt_id}", json=payload(patient_name="Updated Patient"))

    assert response.status_code == 409
    assert response.json()["detail"] == "Cancelled appointments cannot be edited"
    assert client.get(f"/api/appointments/{appt_id}").json()["patient_name"] == "Test Patient"


def test_completed_appointment_cannot_be_updated_or_deleted(client):
    appt_id = client.post("/api/appointments", json=payload()).json()["id"]

    # The test fixture does not expose a status-update endpoint, so seed the
    # terminal status through the database used by this request.
    db = next(app.dependency_overrides[get_db]())
    appt = db.get(models.Appointment, appt_id)
    appt.status = "Completed"
    db.commit()
    db.close()

    update = client.put(f"/api/appointments/{appt_id}", json=payload(patient_name="Updated Patient"))
    assert update.status_code == 409
    assert update.json()["detail"] == "Completed appointments cannot be edited"

    delete = client.delete(f"/api/appointments/{appt_id}")
    assert delete.status_code == 409
    assert delete.json()["detail"] == "Completed appointments cannot be deleted"


def test_completed_appointment_cannot_be_cancelled(client):
    appt_id = client.post("/api/appointments", json=payload()).json()["id"]

    db = next(app.dependency_overrides[get_db]())
    appt = db.get(models.Appointment, appt_id)
    appt.status = "Completed"
    db.commit()
    db.close()

    response = client.post(f"/api/appointments/{appt_id}/cancel")

    assert response.status_code == 409
    assert response.json()["detail"] == "Completed appointments cannot be cancelled"


def test_filters(client):
    client.post("/api/appointments", json=payload(patient_name="Amal Perera", doctor="Dr. A"))
    second = client.post("/api/appointments", json=payload(patient_name="Nimali Fernando", doctor="Dr. B",
                scheduled_at="2030-02-01T10:00", appointment_type="Check-up")).json()
    client.post(f"/api/appointments/{second['id']}/cancel")
    assert len(client.get("/api/appointments", params={"q": "amal"}).json()) == 1
    assert len(client.get("/api/appointments", params={"q": "dr. b"}).json()) == 1
    assert len(client.get("/api/appointments", params={"status": "Cancelled"}).json()) == 1
    assert len(client.get("/api/appointments", params={"appointment_type": "Check-up"}).json()) == 1
    assert len(client.get("/api/appointments", params={"date_from": "2030-02-01"}).json()) == 1
    assert len(client.get("/api/appointments", params={"date_to": "2030-01-31"}).json()) == 1


def test_double_booking_blocked_but_cancelled_slot_reusable(client):
    first = client.post("/api/appointments", json=payload()).json()
    assert client.post("/api/appointments", json=payload(patient_name="Other")).status_code == 409
    # a different doctor at the same time is fine
    assert client.post("/api/appointments", json=payload(doctor="Dr. Other")).status_code == 201
    # editing an appointment without moving it must not conflict with itself
    assert client.put(f"/api/appointments/{first['id']}", json=payload(patient_name="Updated")).status_code == 200
    client.post(f"/api/appointments/{first['id']}/cancel")
    assert client.post("/api/appointments", json=payload(patient_name="Other")).status_code == 201