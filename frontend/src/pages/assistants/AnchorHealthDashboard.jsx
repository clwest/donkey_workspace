import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import useAuthGuard from "../../hooks/useAuthGuard";
import SimpleSparkline from "../../components/assistant/SimpleSparkline";

export default function AnchorHealthDashboard() {
  useAuthGuard();
  const { slug } = useParams();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState("all");
  const [sort, setSort] = useState("score");
  const [orphans, setOrphans] = useState(0);

  const load = async () => {
    setLoading(true);
    try {
      const params = [];
      if (filter !== "all") params.push(`status=${filter}`);
      if (sort) params.push(`sort=${sort}`);
      const query = params.length ? `?${params.join("&")}` : "";
      const data = await apiFetch(`/assistants/${slug}/anchor_health/${query}`);
      const list = data.results || [];
      setRows(list);
      setOrphans(list.filter((r) => r.chunk_count === 0).length);
    } catch (err) {
      console.error("Failed to load anchor health", err);
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [slug, filter]);

  const badgeClass = (score) => {
    if (score >= 0.5) return "bg-danger";
    if (score >= 0.2) return "bg-warning";
    return "bg-success";
  };

  return (
    <div className="container my-5">
      <h2 className="mb-3">
        Anchor Health Dashboard{" "}
        <span className="badge bg-danger">{orphans} Orphaned</span>
      </h2>
      <div className="d-flex gap-2 mb-2">
        <button
          className={`btn btn-sm ${filter === "all" ? "btn-primary" : "btn-outline-primary"}`}
          onClick={() => setFilter("all")}
        >
          All
        </button>
        <button
          className={`btn btn-sm ${filter === "high_drift" ? "btn-primary" : "btn-outline-primary"}`}
          onClick={() => setFilter("high_drift")}
        >
          High Drift
        </button>
        <button
          className={`btn btn-sm ${filter === "pending_mutation" ? "btn-primary" : "btn-outline-primary"}`}
          onClick={() => setFilter("pending_mutation")}
        >
          Needs Mutation
        </button>
        <button
          className={`btn btn-sm ${filter === "no_match" ? "btn-primary" : "btn-outline-primary"}`}
          onClick={() => setFilter("no_match")}
        >
          Low Match
        </button>
        <button
          className="btn btn-outline-secondary ms-auto"
          onClick={load}
          disabled={loading}
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
        <button
          className="btn btn-outline-primary"
          onClick={() =>
            apiFetch("/dev/cli/run/", {
              method: "POST",
              body: {
                command: "export_assistant_trust_index",
                flags: `--assistant ${slug}`,
              },
            })
          }
        >
          📤 Export Drift Status
        </button>
        <select
          className="form-select form-select-sm w-auto"
          value={sort}
          onChange={(e) => setSort(e.target.value)}
        >
          <option value="score">Score</option>
          <option value="uses">Uses</option>
          <option value="fallback_rate">Fallback Rate</option>
        </select>
      </div>
      <table className="table table-sm table-bordered">
        <thead className="table-light">
          <tr>
            <th>Anchor Term</th>
            <th>Avg Score</th>
            <th>Uses</th>
            <th>Fallback %</th>
            <th>Mutation</th>
            <th>Reinforced</th>
            <th>Drift</th>
            <th>Trend</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.slug} className={r.is_unstable ? "table-warning" : ""}>
              <td>{r.label}</td>
              <td>{r.avg_score?.toFixed(2)}</td>
              <td>{r.uses}</td>
              <td>{(r.fallback_rate * 100).toFixed(0)}%</td>
              <td>{r.mutation_status}</td>
              <td>{r.reinforcement_count}</td>
              <td>
                <span className={`badge ${badgeClass(r.drift_score)}`}>
                  {r.drift_score.toFixed(2)}
                </span>
              </td>
              <td>
                <SimpleSparkline data={r.trend || []} />
              </td>
            </tr>
          ))}
          {rows.length === 0 && !loading && (
            <tr>
              <td colSpan="7" className="text-muted">
                No anchors found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
