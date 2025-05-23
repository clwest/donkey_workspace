import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AgentCodexMonitor() {
  const [codices, setCodices] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agent-codices/");
        setCodices(res.results || res);
      } catch (err) {
        console.error("Failed to load agent codices", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Agent Codex Awareness</h5>
      <ul className="list-group">
        {codices.map((c) => (
          <li key={c.id} className="list-group-item">
            <strong>{c.base_codex}</strong> – trend: {c.sentiment_trend}
          </li>
        ))}
        {codices.length === 0 && (
          <li className="list-group-item text-muted">No codex data.</li>
        )}
      </ul>
    </div>
  );
}
