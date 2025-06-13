import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ToolIndexPanel() {
  const [tools, setTools] = useState([]);
  const [assistant, setAssistant] = useState("");
  const [type, setType] = useState("");

  useEffect(() => {
    const params = new URLSearchParams();
    if (assistant) params.append("assistant", assistant);
    if (type) params.append("type", type);
    apiFetch(`/tools/index/?${params.toString()}`)
      .then((res) => setTools(res.results || []))
      .catch(() => setTools([]));
  }, [assistant, type]);

  return (
    <div className="container mt-3">
      <h3>Tool Index</h3>
      <div className="d-flex gap-2 mb-2">
        <input
          type="text"
          className="form-control w-auto"
          placeholder="Filter assistant"
          value={assistant}
          onChange={(e) => setAssistant(e.target.value)}
        />
        <input
          type="text"
          className="form-control w-auto"
          placeholder="Tool tag"
          value={type}
          onChange={(e) => setType(e.target.value)}
        />
      </div>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Name</th>
            <th>Slug</th>
            <th>Version</th>
            <th>Public</th>
            <th>Last Used</th>
            <th>Exec Count</th>
            <th>Assistants</th>
          </tr>
        </thead>
        <tbody>
          {tools.map((t) => (
            <tr key={t.id}>
              <td>{t.name}</td>
              <td>{t.slug}</td>
              <td>{t.version || "-"}</td>
              <td>{t.is_public ? "yes" : "no"}</td>
              <td>{t.last_used_at ? new Date(t.last_used_at).toLocaleString() : "-"}</td>
              <td>{t.exec_count}</td>
              <td>{t.assistants.join(", ")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
