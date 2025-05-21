export default function CrossThreadRecallPanel({ entries }) {
  if (!entries || entries.length === 0) {
    return (
      <div className="alert alert-secondary mt-3">No related memories.</div>
    );
  }

  return (
    <div className="mt-3">
      <h5>Recalled Memories</h5>
      <ul className="list-group">
        {entries.map((m) => (
          <li key={m.id} className="list-group-item">
            {m.summary || m.event}
          </li>
        ))}
      </ul>
    </div>
  );
}
