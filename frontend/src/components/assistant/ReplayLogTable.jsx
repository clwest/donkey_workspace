import DriftBadge from "./DriftBadge";

export default function ReplayLogTable({ logs, slug, onView }) {
  return (
    <table className="table table-sm table-bordered">
      <thead className="table-light">
        <tr>
          <th>Date</th>
          <th>Drift</th>
          <th>Count</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {logs.map((log) => (
          <tr key={log.id}>
            <td>{new Date(log.created_at).toLocaleString()}</td>
            <td><DriftBadge score={log.drift_score} /></td>
            <td>{log.summary_count}</td>
            <td>
              <button className="btn btn-sm btn-outline-primary" onClick={() => onView(log.id)}>
                View
              </button>
            </td>
          </tr>
        ))}
        {logs.length === 0 && (
          <tr>
            <td colSpan="4" className="text-muted text-center">
              No replay logs.
            </td>
          </tr>
        )}
      </tbody>
    </table>
  );
}
