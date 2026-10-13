import { useState } from "react";
import { STATUSES, TYPES } from "./consants";

const EMPTY = { patient_name: "", scheduled_at: "", doctor: "", appointment_type: TYPES[0], status: STATUSES[0] };

export default function AppointmentForm({ initial, onSubmit, onCancel }) {
  const [form, setForm] = useState(initial ? { ...initial, scheduled_at: initial.scheduled_at.slice(0, 16) } : EMPTY);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
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
    <form className="card form" onSubmit={handleSubmit}>
      <h2>{initial ? "Edit appointment" : "New appointment"}</h2>
      <label>Patient name
        <input required maxLength={100} value={form.patient_name} onChange={set("patient_name")} />
      </label>
      <label>Doctor
        <input required maxLength={100} value={form.doctor} onChange={set("doctor")} />
      </label>
      <label>Date & time
        <input required type="datetime-local" value={form.scheduled_at} onChange={set("scheduled_at")} />
      </label>
      <label>Type
        <select value={form.appointment_type} onChange={set("appointment_type")}>
          {TYPES.map((t) => <option key={t}>{t}</option>)}
        </select>
      </label>
      <label>Status
        <select value={form.status} onChange={set("status")}>
          {STATUSES.map((s) => <option key={s}>{s}</option>)}
        </select>
      </label>
      {error && <p className="error" role="alert">{error}</p>}
      <div className="actions">
        <button type="submit" disabled={saving}>{saving ? "Saving…" : "Save"}</button>
        <button type="button" className="secondary" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}