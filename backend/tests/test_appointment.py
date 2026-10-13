import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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
            "appointment_type": "Consultation", "status": "Scheduled"}
    return {**base, **overrides}


def test_create_and_get(client):
    r = client.post("/api/appointments", json=payload())
    assert r.status_code == 201
    created = r.json()
    assert client.get(f"/api/appointments/{created['id']}").json()["patient_name"] == "Test Patient"


def test_list_sorted_by_time(client):
    client.post("/api/appointments", json=payload(scheduled_at="2030-01-11T09:00"))
    client.post("/api/appointments", json=payload(scheduled_at="2030-01-10T09:00"))
    times = [a["scheduled_at"] for a in client.get("/api/appointments").json()]
    assert times == sorted(times)


def test_update(client):
    appt_id = client.post("/api/appointments", json=payload()).json()["id"]
    r = client.put(f"/api/appointments/{appt_id}", json=payload(status="Completed"))
    assert r.status_code == 200 and r.json()["status"] == "Completed"


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


def test_filters(client):
    client.post("/api/appointments", json=payload(patient_name="Amal Perera", doctor="Dr. A"))
    client.post("/api/appointments", json=payload(patient_name="Nimali Fernando", doctor="Dr. B",
                scheduled_at="2030-02-01T10:00", status="Completed", appointment_type="Check-up"))
    assert len(client.get("/api/appointments", params={"q": "amal"}).json()) == 1
    assert len(client.get("/api/appointments", params={"q": "dr. b"}).json()) == 1
    assert len(client.get("/api/appointments", params={"status": "Completed"}).json()) == 1
    assert len(client.get("/api/appointments", params={"appointment_type": "Check-up"}).json()) == 1
    assert len(client.get("/api/appointments", params={"date_from": "2030-02-01"}).json()) == 1
    assert len(client.get("/api/appointments", params={"date_to": "2030-01-31"}).json()) == 1


def test_double_booking_blocked_but_cancelled_slot_reusable(client):
    first = client.post("/api/appointments", json=payload()).json()
    assert client.post("/api/appointments", json=payload(patient_name="Other")).status_code == 409
    # a different doctor at the same time is fine
    assert client.post("/api/appointments", json=payload(doctor="Dr. Other")).status_code == 201
    # editing an appointment without moving it must not conflict with itself
    assert client.put(f"/api/appointments/{first['id']}", json=payload(status="Completed")).status_code == 200
    client.put(f"/api/appointments/{first['id']}", json=payload(status="Cancelled"))
    assert client.post("/api/appointments", json=payload(patient_name="Other")).status_code == 201