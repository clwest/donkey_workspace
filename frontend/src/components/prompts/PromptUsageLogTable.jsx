// components/prompts/PromptUsageLogTable.jsx

export default function PromptUsageLogTable({ logs }) {

    if (!logs?.length) return <p className="text-muted">No usage history available.</p>;
    return (
      <div className="mt-4">
        <h5>📜 Prompt Usage History</h5>
        <table className="table table-bordered table-sm">
          <thead className="table-light">
            <tr>
              <th>Date</th>
              <th>Used By</th>
              <th>Purpose</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>{new Date(log.created_at).toLocaleString()}</td>
                <td>{log.used_by}</td>
                <td>{log.purpose || "—"}</td>
                <td className="text-truncate" style={{ maxWidth: 300 }}>
                  {log.result_output || "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
}
