import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

export default function KeeperLogViewer() {
  const [logs, setLogs] = useState([]);
  const [assistants, setAssistants] = useState([]);
  const [assistant, setAssistant] = useState("");
  const [action, setAction] = useState("");
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    apiFetch("/assistants/")
      .then((res) => setAssistants(res.results || res))
      .catch(() => setAssistants([]));
  }, []);

  useEffect(() => {
    const params = new URLSearchParams();
    if (assistant) params.set("assistant", assistant);
    if (action) params.set("action", action);
    apiFetch(`/keeper/logs/?${params.toString()}`)
      .then((res) => setLogs(res.results || res))
      .catch(() => setLogs([]));
  }, [assistant, action]);

  const badgeClass = (act) => {
    if (act === "suggest_mutation") return "bg-info text-dark";
    if (act === "reflection_written") return "bg-success";
    return "bg-secondary";
  };

  return (
    <div className="container my-4">
      <h1 className="mb-3">Keeper Logs</h1>
      <div className="d-flex gap-2 mb-3">
        <select
          className="form-select form-select-sm"
          style={{ maxWidth: "200px" }}
          value={assistant}
          onChange={(e) => setAssistant(e.target.value)}
        >
          <option value="">All Assistants</option>
          {assistants.map((a) => (
            <option key={a.slug} value={a.slug}>
              {a.name}
            </option>
          ))}
        </select>
        <select
          className="form-select form-select-sm"
          style={{ maxWidth: "200px" }}
          value={action}
          onChange={(e) => setAction(e.target.value)}
        >
          <option value="">All Actions</option>
          <option value="suggest_mutation">suggest_mutation</option>
          <option value="reflection_written">reflection_written</option>
        </select>
      </div>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Assistant</th>
            <th>Anchor</th>
            <th>Action</th>
            <th>Suggested Label</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <>
              <tr
                key={log.id}
                onClick={() =>
                  setExpanded(expanded === log.id ? null : log.id)
                }
                style={{ cursor: "pointer" }}
              >
                <td>{new Date(log.timestamp).toLocaleString()}</td>
                <td>{log.assistant_slug || ""}</td>
                <td>
                  <Link to={`/anchor/symbolic/${log.anchor_slug}`}>{log.anchor_label}</Link>
                </td>
                <td>
                  <span className={`badge ${badgeClass(log.action_taken)}`}>
                    {log.action_taken}
                  </span>
                </td>
                <td>{log.suggested_label || ""}</td>
              </tr>
              {expanded === log.id && (
                <tr key={`${log.id}-exp`}>
                  <td colSpan="5" className="bg-light">
                    {log.notes || "No notes"}
                    {log.memory_id && (
                      <div className="mt-2">
                        <Link to={`/memory/${log.memory_id}`}>View Memory</Link>
                      </div>
                    )}
                  </td>
                </tr>
              )}
            </>
          ))}
          {logs.length === 0 && (
            <tr>
              <td colSpan="5" className="text-muted">
                No logs found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
