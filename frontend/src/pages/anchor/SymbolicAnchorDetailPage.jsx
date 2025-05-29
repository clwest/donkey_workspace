import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import { fetchAnchorConvergence } from "../../api/agents";

export default function SymbolicAnchorDetailPage() {
  const { slug } = useParams();
  const [anchor, setAnchor] = useState(null);
  const [summary, setSummary] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch("/memory/symbolic-anchors/");
        const anchors = data.results || data;
        const found = anchors.find((a) => a.slug === slug);
        setAnchor(found);
        const logsData = await fetchAnchorConvergence(slug);
        const logs = logsData.results || logsData;
        const by = {};
        logs.forEach((l) => {
          if (!by[l.assistant]) {
            by[l.assistant] = {
              name: l.assistant_name,
              last: l.created_at,
              count: 0,
              score: 0,
            };
          }
          const b = by[l.assistant];
          b.count += 1;
          b.score += l.final_score;
          if (new Date(l.created_at) > new Date(b.last)) {
            b.last = l.created_at;
          }
        });
        setSummary(Object.values(by));
      } catch (err) {
        console.error("Failed to load anchor detail", err);
      } finally {
        setLoading(false);
      }
    }
    if (slug) load();
  }, [slug]);

  if (loading) return <div className="container my-4">Loading...</div>;
  if (!anchor) return <div className="container my-4">Anchor not found.</div>;

  return (
    <div className="container my-4">
      <h1 className="mb-3">{anchor.label}</h1>
      {anchor.description && <p className="mb-4">{anchor.description}</p>}
      <h5>Reinforced By</h5>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Assistant</th>
            <th>Last Convergence</th>
            <th>Attempts</th>
            <th>Avg Score</th>
          </tr>
        </thead>
        <tbody>
          {summary.map((s) => (
            <tr key={s.name}>
              <td>{s.name}</td>
              <td>{new Date(s.last).toLocaleString()}</td>
              <td>{s.count}</td>
              <td>{(s.score / s.count).toFixed(2)}</td>
            </tr>
          ))}
          {summary.length === 0 && (
            <tr>
              <td colSpan="4" className="text-muted">
                No reinforcement events.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
