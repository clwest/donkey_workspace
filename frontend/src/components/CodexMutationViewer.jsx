import { useEffect, useState } from "react";
import { fetchDialogueMutations } from "../api/agents";

export default function CodexMutationViewer() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetchDialogueMutations()
      .then((res) => setLogs(res.results || res))
      .catch(() => setLogs([]));
  }, []);

  return (
    <div className="p-2 border rounded">
      <h5>Dialogue Mutations</h5>
      <ul className="list-group">
        {logs.map((l) => (
          <li key={l.id} className="list-group-item">
            {l.mutation_reason}
          </li>
        ))}
        {logs.length === 0 && (
          <li className="list-group-item text-muted">No mutations.</li>
        )}
      </ul>
    </div>
  );
}
