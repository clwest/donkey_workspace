import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import HintBubble from "../../components/HintBubble";
import useAssistantHints from "../../hooks/useAssistantHints";
import TourProgressBar from "../../components/onboarding/TourProgressBar";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function GlossaryConvergencePage() {
  useAuthGuard();
  const { slug } = useParams();
  const { hints, dismissHint } = useAssistantHints(slug);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState({ applied: 0, reviewed: 0 });
  const [query, setQuery] = useState("");
  const [orderBy, setOrderBy] = useState("label");

  const load = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (query) params.set("q", query);
      if (orderBy) params.set("order_by", orderBy);
      const data = await apiFetch(
        `/assistants/${slug}/glossary/convergence/?${params.toString()}`
      );
      const anchors = data.anchor_stats || [];
      setRows(anchors);
      const reviewed = anchors.filter((a) => a.mutation_status !== "pending").length;
      const applied = anchors.filter((a) => a.mutation_status === "applied").length;
      setSummary({ applied, reviewed });
    } catch (err) {
      console.error("Failed to load convergence", err);
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [slug, query, orderBy]);

  return (
    <div className="container my-5">
      <h2 className="mb-3">Glossary Convergence</h2>
      <TourProgressBar assistantSlug={slug} />
      <div className="mb-2 d-flex gap-2">
        <input
          className="form-control"
          placeholder="Search terms"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select
          className="form-select w-auto"
          value={orderBy}
          onChange={(e) => setOrderBy(e.target.value)}
        >
          <option value="label">Label A-Z</option>
          <option value="-label">Label Z-A</option>
          <option value="-fallback_score">Fallback ↓</option>
          <option value="fallback_score">Fallback ↑</option>
        </select>
      </div>
      <div className="d-flex justify-content-end gap-2 mb-2">
        <Link
          to={`/anchor/symbolic?assistant=${slug}`}
          className="btn btn-sm btn-outline-secondary"
        >
          🧠 Symbolic Glossary Editor
        </Link>
        <Link
          to={`/anchor/mutations?assistant=${slug}`}
          className="btn btn-sm btn-outline-primary"
        >
          🧪 Review Mutation Suggestions
        </Link>
      </div>
      <button className="btn btn-outline-primary mb-3" onClick={load} disabled={loading}>
        {loading ? "Refreshing..." : "Refresh"}
      </button>
      <div className="mb-2">
        <span className="badge bg-success me-2">Applied {summary.applied}</span>
        <span className="badge bg-secondary">Reviewed {summary.reviewed}</span>
      </div>
      <table className="table table-sm table-bordered">
        <thead className="table-light">
          <tr>
            <th>Anchor Term</th>
            <th>Status</th>
            <th>Drift Risk</th>
            <th>Source</th>
            <th>Last Match Score</th>
            <th>Change</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.label}>
              <td
                dangerouslySetInnerHTML={{
                  __html: query
                    ? r.label.replace(new RegExp(`(${query})`, 'i'), '<b>$1</b>')
                    : r.label,
                }}
              />
              <td>{r.status}</td>
              <td>{r.risk || "-"}</td>
              <td>{r.mutation_source || r.source || "-"}</td>
              <td>{r.avg_score?.toFixed(2)}</td>
              <td>{r.change}</td>
            </tr>
          ))}
          {rows.length === 0 && !loading && (
            <tr>
              <td colSpan="6" className="text-muted">
                No anchors found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
      {hints.find((h) => h.id === "glossary_tour" && !h.dismissed) && (
        <HintBubble
          content={hints.find((h) => h.id === "glossary_tour").content}
          position={{ top: 80, right: 20 }}
          onDismiss={() => dismissHint("glossary_tour")}
        />
      )}
    </div>
  );
}
