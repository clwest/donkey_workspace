import React from "react";
import { useGroupedReflectionHistory } from "../../hooks/useGroupedReflectionHistory"

export default function GroupedReflectionHistoryPanel() {
  const { history, loading } = useGroupedReflectionHistory();

  return (
    <div className="mt-4 p-3 border rounded bg-white">
      <h5>🕘 Past Grouped Reflections</h5>
      {loading ? (
        <p>Loading history...</p>
      ) : history.length === 0 ? (
        <p>No past grouped reflections found.</p>
      ) : (
        <ul className="list-group">
          {history.map((r) => (
            <li key={r.id} className="list-group-item">
              <strong>{new Date(r.created_at).toLocaleString()}</strong>
              <br />
              <span className="text-muted small">{r.summary}</span>
              <br />
              <a
                href={`/grouped-reflection/${r.id}`}
                className="btn btn-sm btn-outline-primary mt-2"
              >
                View Full Reflection
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
