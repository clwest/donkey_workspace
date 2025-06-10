import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import { Link } from "react-router-dom";

export default function DemoCheckupPage() {
  const [rows, setRows] = useState(null);

  useEffect(() => {
    apiFetch("/assistants/demo_checkup/")
      .then((data) => setRows(Array.isArray(data) ? data : []))
      .catch(() => setRows([]));
  }, []);

  if (rows === null) {
    return <div className="container py-5">Loading...</div>;
  }

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between mb-3">
        <h2>Demo Assistant Checkup</h2>
        <Link to="/dev-dashboard" className="btn btn-outline-secondary">
          ← Back to Dev Dashboard
        </Link>
      </div>
      <div className="table-responsive">
        <table className="table table-sm table-bordered">
          <thead className="table-light">
            <tr>
              <th>Slug</th>
              <th>Name</th>
              <th>Prompt</th>
              <th>Context</th>
              <th>Memories</th>
              <th>Reflections</th>
              <th>Starters</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.slug} title={r.prompt_preview}>
                <td>{r.slug}</td>
                <td>{r.name}</td>
                <td>{r.has_system_prompt ? "✅" : "❌"}</td>
                <td>{r.has_memory_context ? "✅" : "❌"}</td>
                <td>{r.memory_count}</td>
                <td>{r.reflection_count}</td>
                <td>{r.starter_chat_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
