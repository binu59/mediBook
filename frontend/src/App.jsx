import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import { STATUSES, TYPES } from "./consants.js";
import AppointmentForm from "./AppointmentForm";
import AppointmentTable from "./AppointmentTable";

const NO_FILTERS = { q: "", status: "", appointment_type: "", date_from: "", date_to: "" };

export default function App() {
  const [appointments, setAppointments] = useState([]);
  const [filters, setFilters] = useState(NO_FILTERS);
  const [editing, setEditing] = useState({});
  const [showHistory, setShowHistory] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      setAppointments(await api.list(filters));
      setError("");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // debounce so typing in the search box doesn't fire a request per keystroke
  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
  }, [load]);

  const setFilter = (field) => (e) => setFilters({ ...filters, [field]: e.target.value });

  async function handleSave(data) {
    if (editing.id) await api.update(editing.id, data);
    else await api.create(data);
    await load();
    setEditing({});
    setShowHistory(true);
  }

  async function handleCancel(a) {
    if (a.status === "Cancelled" || !window.confirm(`Cancel ${a.patient_name}'s appointment?`)) return;
    try {
      await api.cancel(a.id);
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="MediBook home">
          <span className="brand-mark">+</span>
          <span>Medi<span>Book</span></span>
        </a>
        <nav className="topnav" aria-label="Main navigation">
          <button className={!showHistory ? "nav-link active" : "nav-link"} onClick={() => setShowHistory(false)}>Book an appointment</button>
          <button className={showHistory ? "nav-link active" : "nav-link"} onClick={() => setShowHistory(true)}>My appointments{appointments.length > 0 && <span className="count">{appointments.length}</span>}</button>
        </nav>
        <div className="profile">
          <span className="avatar">M</span>
          <span className="profile-name">Mewanya</span>
          <span className="profile-chevron">⌄</span>
        </div>
      </header>

      {!showHistory && (
        <section className="welcome">
          <div>
            <p className="eyebrow">YOUR HEALTH, YOUR WAY</p>
            <h1>Good morning, Mewanya</h1>
            <p className="welcome-copy">Find the right care for you and book a session in just a few clicks.</p>
          </div>
          <div className="welcome-orb" aria-hidden="true"><span>✚</span></div>
        </section>
      )}

      {showHistory ? (
        <section className="history-view">
          <div className="section-heading">
            <div>
              <p className="eyebrow">YOUR CARE JOURNEY</p>
              <h2>My appointments</h2>
            </div>
            <button onClick={() => { setShowHistory(false); setEditing({}); }}>+ Book an appointment</button>
          </div>
          <section className="card filters">
            <input placeholder="Search patient or doctor…" value={filters.q} onChange={setFilter("q")} />
            <select value={filters.status} onChange={setFilter("status")}>
              <option value="">All statuses</option>
              {STATUSES.map((s) => <option key={s}>{s}</option>)}
            </select>
            <select value={filters.appointment_type} onChange={setFilter("appointment_type")}>
              <option value="">All types</option>
              {TYPES.map((t) => <option key={t}>{t}</option>)}
            </select>
            <input type="date" aria-label="From date" value={filters.date_from} onChange={setFilter("date_from")} />
            <input type="date" aria-label="To date" value={filters.date_to} onChange={setFilter("date_to")} />
            <button className="secondary" onClick={() => setFilters(NO_FILTERS)}>Clear</button>
          </section>
          {error && <p className="error" role="alert">{error}</p>}
          {loading ? <p className="loading">Loading your appointments…</p> : <AppointmentTable appointments={appointments} onEdit={(a) => { setEditing(a); setShowHistory(false); }} onCancel={handleCancel} />}
        </section>
      ) : (
        <AppointmentForm
          key={editing?.id ?? "new"}
          initial={editing.id ? editing : null}
          onSubmit={handleSave}
          onCancel={() => setEditing({})}
        />
      )}
      <footer><span>© 2026 MediBook</span><span>Care that fits your life.</span></footer>
    </main>
  );
}