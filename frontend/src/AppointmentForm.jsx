import { useState } from "react";
import { DOCTORS, TYPES } from "./consants";

const EMPTY = { patient_name: "", scheduled_at: "", doctor: "", appointment_type: TYPES[0] };

export default function AppointmentForm({ initial, onSubmit, onCancel }) {
  const [form, setForm] = useState(initial ? {
    patient_name: initial.patient_name,
    scheduled_at: initial.scheduled_at.slice(0, 16),
    doctor: initial.doctor,
    appointment_type: initial.appointment_type,
  } : EMPTY);
  const [doctorQuery, setDoctorQuery] = useState(initial?.doctor ?? "");
  const [doctorOpen, setDoctorOpen] = useState(false);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });
  const setScheduledPart = (part) => (e) => {
    const [date = "", time = ""] = form.scheduled_at.split("T");
    setForm({ ...form, scheduled_at: part === "date" ? `${e.target.value}T${time}` : `${date}T${e.target.value}` });
  };
  const matchingDoctors = DOCTORS.filter((doctor) => {
    const query = doctorQuery.trim().toLowerCase();
    return !query || `${doctor.name} ${doctor.specialty}`.toLowerCase().includes(query);
  });

  function chooseDoctor(doctor) {
    setForm({ ...form, doctor: doctor.name });
    setDoctorQuery(doctor.name);
    setDoctorOpen(false);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!DOCTORS.some((doctor) => doctor.name === form.doctor)) {
      setError("Please select a doctor from the list.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      await onSubmit(form);
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  }

  return (
    <form className="booking-layout" onSubmit={handleSubmit}>
      <div className="booking-card">
        <div className="form-heading">
          <div>
            <p className="eyebrow">TAKE THE NEXT STEP</p>
            <h2>{initial ? "Edit appointment" : "Book your appointment"}</h2>
            <p>Tell us a little about your visit and we’ll reserve the right time for you.</p>
          </div>
          <div className="form-icon" aria-hidden="true">✚</div>
        </div>
        <div className="form">
          <label>Patient name
            <input required maxLength={100} placeholder="e.g. mewanya" value={form.patient_name} onChange={set("patient_name")} />
          </label>
          <label className="doctor-field">Doctor
            <div className="doctor-picker">
              <input
                required
                role="combobox"
                aria-autocomplete="list"
                aria-expanded={doctorOpen}
                aria-controls="doctor-options"
                maxLength={100}
                placeholder="Search by doctor or specialty"
                value={doctorQuery}
                onClick={() => setDoctorOpen(true)}
                onBlur={() => setTimeout(() => setDoctorOpen(false), 0)}
                onChange={(e) => {
                  setDoctorQuery(e.target.value);
                  setForm({ ...form, doctor: "" });
                  setDoctorOpen(true);
                }}
              />
              {doctorOpen && (
                <div id="doctor-options" className="doctor-options" role="listbox">
                  {matchingDoctors.length ? matchingDoctors.map((doctor) => (
                    <button
                      type="button"
                      className="doctor-option"
                      role="option"
                      aria-selected={form.doctor === doctor.name}
                      key={doctor.name}
                      onMouseDown={(e) => e.preventDefault()}
                      onClick={() => chooseDoctor(doctor)}
                    >
                      <span className="doctor-avatar">{doctor.name.replace("Dr. ", "").charAt(0)}</span>
                      <span className="doctor-details">
                        <strong>{doctor.name}</strong>
                        <small>{doctor.specialty}</small>
                      </span>
                    </button>
                  )) : <p className="doctor-empty">No doctors match your search.</p>}
                </div>
              )}
            </div>
            <small className="field-hint">Choose a doctor to see their specialty.</small>
          </label>
          <div className="date-time-fields">
            <label>Date
              <input required type="date" value={form.scheduled_at.split("T")[0]} onChange={setScheduledPart("date")} />
            </label>
            <label>Time
              <input required type="time" value={form.scheduled_at.split("T")[1] ?? ""} onChange={setScheduledPart("time")} />
            </label>
          </div>
          <label>Appointment type
            <select value={form.appointment_type} onChange={set("appointment_type")}>
              {TYPES.map((t) => <option key={t}>{t}</option>)}
            </select>
          </label>
        </div>
        <div className="visit-intent">
          <p>What kind of care do you need?</p>
          <div className="intent-chips">
            {TYPES.map((type) => <button type="button" className={form.appointment_type === type ? "intent-chip selected" : "intent-chip"} key={type} onClick={() => setForm({ ...form, appointment_type: type })}>{type}</button>)}
          </div>
        </div>
      {error && <p className="error" role="alert">{error}</p>}
        <div className="actions">
          <button type="submit" disabled={saving}>{saving ? "Booking…" : initial ? "Save changes" : "Book appointment"} <span></span></button>
          {initial && <button type="button" className="secondary" onClick={onCancel}>Cancel</button>}
        </div>
        <p className="secure-note"> Your information is private and secure</p>
      </div>
      <aside className="booking-aside">
        <div className="aside-badge">✦</div>
        <h3>Care made simple.</h3>
        <p>Connect with trusted healthcare professionals and take control of your wellbeing.</p>
        <div className="aside-stat"><strong>4.9/5</strong><span>patient satisfaction</span></div>
        <div className="aside-stat"><strong>24/7</strong><span>care when you need it</span></div>
      </aside>
    </form>
  );
}