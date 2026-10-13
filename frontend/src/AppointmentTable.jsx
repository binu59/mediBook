const fmt = (iso) => new Date(iso).toLocaleString([], { dateStyle: "medium", timeStyle: "short" });

export default function AppointmentTable({ appointments, onEdit, onDelete }) {
  if (!appointments.length) return <p className="empty">No appointments found.</p>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr><th>Patient</th><th>Date & time</th><th>Doctor</th><th>Type</th><th>Status</th><th /></tr>
        </thead>
        <tbody>
          {appointments.map((a) => (
            <tr key={a.id}>
              <td>{a.patient_name}</td>
              <td>{fmt(a.scheduled_at)}</td>
              <td>{a.doctor}</td>
              <td>{a.appointment_type}</td>
              <td><span className={`badge ${a.status.toLowerCase().replace(" ", "")}`}>{a.status}</span></td>
              <td className="row-actions">
                <button className="secondary" onClick={() => onEdit(a)}>Edit</button>
                <button className="danger" onClick={() => onDelete(a)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}