import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function DemoFeedbackExplorer() {
  useAuthGuard();
  const [logs, setLogs] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [rating, setRating] = useState("");
  const [converted, setConverted] = useState(false);
  const [demoSlug, setDemoSlug] = useState("");
  const [demos, setDemos] = useState([]);

  useEffect(() => {
    apiFetch("/assistants/demos/")
      .then((res) => setDemos(Array.isArray(res) ? res : []))
      .catch(() => setDemos([]));
  }, []);

  useEffect(() => {
    load(1);
  }, [rating, converted, demoSlug]);

  const load = async (p) => {
    const params = { page: p };
    if (rating) params.rating = rating;
    if (converted) params.converted = true;
    if (demoSlug) params.demo_slug = demoSlug;
    const res = await apiFetch("/assistants/demo_feedback/", { params });
    setLogs(res.results || []);
    setCount(res.count || 0);
    setPage(p);
  };

  const pages = Math.ceil(count / 20);

  function exportCSV() {
    const header = [
      "demo_slug",
      "session_id",
      "rating",
      "feedback_text",
      "interaction_score",
      "converted",
      "message_count",
      "starter_query",
      "helpful_tips",
      "timestamp",
    ];
    const rows = logs.map((l) => [
      l.demo_slug,
      l.session_id,
      l.rating || "",
      l.feedback_text ? l.feedback_text.replace(/"/g, '""') : "",
      l.interaction_score,
      l.converted ? "1" : "0",
      l.message_count,
      l.starter_query ? l.starter_query.replace(/"/g, '""') : "",
      l.helpful_tips,
      l.timestamp,
    ]);
    const csv = [header.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "demo_feedback.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between mb-3">
        <h2>Demo Feedback Explorer</h2>
        <div>
          <button className="btn btn-outline-secondary me-2" onClick={exportCSV}>
            Export CSV
          </button>
          <Link to="/assistants/demos/insights" className="btn btn-secondary">
            ← Back to Insights
          </Link>
        </div>
      </div>
      <div className="row g-2 mb-3">
        <div className="col-md-3">
          <label className="form-label">Demo</label>
          <select
            className="form-select"
            value={demoSlug}
            onChange={(e) => setDemoSlug(e.target.value)}
          >
            <option value="">All</option>
            {demos.map((d) => (
              <option key={d.demo_slug} value={d.demo_slug}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
        <div className="col-md-3">
          <label className="form-label">Rating</label>
          <select
            className="form-select"
            value={rating}
            onChange={(e) => setRating(e.target.value)}
          >
            <option value="">All</option>
            {[1, 2, 3, 4, 5].map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </div>
        <div className="col-md-3 d-flex align-items-end">
          <div className="form-check form-switch">
            <input
              type="checkbox"
              className="form-check-input"
              id="convertedOnly"
              checked={converted}
              onChange={(e) => setConverted(e.target.checked)}
            />
            <label className="form-check-label ms-2" htmlFor="convertedOnly">
              Converted Only
            </label>
          </div>
        </div>
      </div>
      <div className="table-responsive">
        <table className="table table-sm table-bordered">
          <thead className="table-light">
            <tr>
              <th>Demo</th>
              <th>Stars</th>
              <th>Msgs</th>
              <th>Conv</th>
              <th>Feedback</th>
              <th>Starter</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <>
                <tr
                  key={log.id}
                  className={
                    log.rating <= 2 && log.interaction_score > 5
                      ? "table-warning"
                      : ""
                  }
                >
                  <td>{log.demo_slug}</td>
                  <td>{"★".repeat(log.rating || 0)}</td>
                  <td>{log.message_count}</td>
                  <td>{log.converted ? "✅" : "❌"}</td>
                  <td>{log.feedback_text.slice(0, 30)}</td>
                  <td title={log.starter_query}>ℹ️</td>
                  <td>{new Date(log.timestamp).toLocaleString()}</td>
                </tr>
                <tr>
                  {log.feedback_text && (
                    <td colSpan="7" className="small text-muted">
                      {log.feedback_text}
                    </td>
                  )}
                </tr>
              </>
            ))}
          </tbody>
        </table>
      </div>
      {pages > 1 && (
        <div className="mt-2">
          <nav>
            <ul className="pagination pagination-sm">
              {Array.from({ length: pages }, (_, i) => i + 1).map((p) => (
                <li key={p} className={"page-item" + (p === page ? " active" : "")}> 
                  <button className="page-link" onClick={() => load(p)}>
                    {p}
                  </button>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      )}
    </div>
  );
}
