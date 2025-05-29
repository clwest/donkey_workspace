import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";
import { fetchAnchorConvergence } from "../../../api/agents";

export default function AssistantGlossaryTrainingPanel({ assistantSlug }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!assistantSlug) return;
    async function load() {
      try {
        const data = await apiFetch("/memory/symbolic-anchors/");
        const all = data.results || data;
        const reinforced = all.filter((a) => a.reinforced_by?.includes(assistantSlug));

        const lists = await Promise.all(
          reinforced.map((a) =>
            fetchAnchorConvergence(a.slug, assistantSlug)
              .then((d) => (d.results || d).map((l) => ({ ...l, anchor_label: a.label, anchor_slug: a.slug })))
              .catch(() => [])
          )
        );

        const combined = lists.flat().sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setLogs(combined);
      } catch (err) {
        console.error("Failed to fetch anchors", err);
        setLogs([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [assistantSlug]);

  if (loading) return <div>Loading glossary training...</div>;

  if (logs.length === 0) {
    return (
      <div className="text-muted">
        No convergence events yet. Ask your assistant to use glossary definitions more often!
      </div>
    );
  }

  const prev = {};

  return (
    <table className="table table-sm">
      <thead>
        <tr>
          <th>Date</th>
          <th>Anchor</th>
          <th>Retry Type</th>
          <th>Guidance Used</th>
          <th>Score Before</th>
          <th>Score After</th>
          <th>Delta</th>
        </tr>
      </thead>
      <tbody>
        {logs.map((log) => {
          const before = prev[log.anchor_slug] ?? log.final_score;
          const delta = log.final_score - before;
          prev[log.anchor_slug] = log.final_score;
          return (
            <tr key={log.id}>
              <td>{new Date(log.created_at).toLocaleString()}</td>
              <td>{log.anchor_label}</td>
              <td>{log.retry_type || "-"}</td>
              <td>{log.guidance_used ? "used" : "ignored"}</td>
              <td>{before.toFixed(2)}</td>
              <td>{log.final_score.toFixed(2)}</td>
              <td>{delta >= 0 ? `+${delta.toFixed(2)}` : delta.toFixed(2)}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
