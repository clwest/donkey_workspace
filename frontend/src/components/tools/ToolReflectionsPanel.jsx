import { useEffect, useState } from "react";
import { fetchToolReflections, runToolReflection } from "../../api/tools";

export default function ToolReflectionsPanel({ toolId }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    if (!toolId) return;
    fetchToolReflections(toolId)
      .then(setLogs)
      .catch(() => setLogs([]));
  }, [toolId]);

  const handleReflect = async () => {
    try {
      await runToolReflection(toolId);
      const data = await fetchToolReflections(toolId);
      setLogs(data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="mt-3">
      <button className="btn btn-sm btn-primary mb-2" onClick={handleReflect}>
        Reflect Now
      </button>
      {logs.length === 0 ? (
        <div>No reflections yet.</div>
      ) : (
        <ul className="list-group">
          {logs.map((r) => (
            <li key={r.id} className="list-group-item">
              <strong>{r.assistant}</strong>{" "}
              <small className="text-muted">
                {new Date(r.created_at).toLocaleDateString()}
              </small>
              <span className="badge bg-secondary ms-2">
                {Math.round(r.confidence_score * 100)}%
              </span>
              <div>{r.reflection}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
