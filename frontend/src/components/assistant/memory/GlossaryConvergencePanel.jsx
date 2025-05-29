import { useEffect, useState } from "react";
import { fetchConvergenceLogs } from "../../../api/agents";

export default function GlossaryConvergencePanel({ assistantId }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!assistantId) return;
    fetchConvergenceLogs(assistantId)
      .then((res) => setLogs(res.results || res))
      .catch((err) => {
        console.error("Failed to load convergence logs", err);
        setLogs([]);
      })
      .finally(() => setLoading(false));
  }, [assistantId]);

  if (loading) return <div>Loading convergence...</div>;
  if (logs.length === 0) {
    return <div className="text-muted">No convergence logs.</div>;
  }

  const prev = {};
  const totals = { reinforced: 0, ignored: 0, retry: 0 };

  return (
    <div className="p-2 border rounded">
      <h5 className="mb-3">Glossary Convergence</h5>
      <ul className="list-group list-unstyled">
        {logs.map((log) => {
          const before = prev[log.anchor_slug] ?? log.final_score;
          const delta = log.final_score - before;
          prev[log.anchor_slug] = log.final_score;
          if (log.guidance_used && delta > 0) totals.reinforced += 1;
          else if (log.guidance_used) totals.ignored += 1;
          if (!log.guidance_used && !log.retried) totals.retry += 1;
          return (
            <li key={log.id} className="mb-2">
              <div>
                <strong>{log.anchor_label}</strong>{" "}
                <span className="badge bg-secondary ms-1">
                  {delta >= 0 ? `+${delta.toFixed(2)}` : delta.toFixed(2)}
                </span>
                {log.retry_type && (
                  <span className="badge bg-info text-dark ms-1">
                    {log.retry_type}
                  </span>
                )}
                {log.guidance_used && delta > 0 && (
                  <span className="badge bg-success ms-1">Reinforced ✅</span>
                )}
              </div>
              {log.memory_summary && (
                <div className="text-muted small">{log.memory_summary}</div>
              )}
            </li>
          );
        })}
      </ul>
      <div className="mt-2 small">
        ✅ {totals.reinforced} · ⚠️ {totals.ignored} · 📌 {totals.retry}
      </div>
    </div>
  );
}
