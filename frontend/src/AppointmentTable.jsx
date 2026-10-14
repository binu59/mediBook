const fmt = (iso) => new Date(iso).toLocaleString([], { dateStyle: "medium", timeStyle: "short" });

export default function AppointmentTable({ appointments, onEdit, onCancel }) {
  if (!appointments.length) return <p className="empty">No appointments found.</p>;
  return (
    <div className="appointment-cards">
      {appointments.map((a) => (
        <article className="appointment-card" key={a.id}>
          <div className="appointment-card-heading">
            <div>
              <p className="appointment-label">APPOINTMENT</p>
              <h3>{a.appointment_type}</h3>
            </div>
            <span className={`badge ${a.status.toLowerCase().replace(" ", "")}`}>{a.status}</span>
          </div>
          <dl className="appointment-details">
            <div><dt>Date & time</dt><dd>{fmt(a.scheduled_at)}</dd></div>
            <div><dt>Doctor</dt><dd>{a.doctor}</dd></div>
            <div><dt>Patient</dt><dd>{a.patient_name}</dd></div>
          </dl>
          <div className="row-actions">
            {!["Cancelled", "Completed"].includes(a.status) && <button className="secondary" onClick={() => onEdit(a)}>Edit appointment</button>}
            {!["Cancelled", "Completed"].includes(a.status) && <button className="danger" onClick={() => onCancel(a)}>Cancel booking</button>}
          </div>
        </article>
      ))}
    </div>
  );
}