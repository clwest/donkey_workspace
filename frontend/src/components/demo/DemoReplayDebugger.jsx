import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function DemoReplayDebugger({ slug, sessionId }) {
  const [data, setData] = useState(null);
  const [tab, setTab] = useState("messages");

  useEffect(() => {
    if (!slug || !sessionId) return;
    apiFetch(`/assistants/${slug}/demo_replay/${sessionId}/`)
      .then(setData)
      .catch(() => setData(null));
  }, [slug, sessionId]);

  if (!data) return null;

  const frames = data.frames || [];

  return (
    <div className="border rounded p-3 mt-3">
      <h5 className="mb-2">Demo Replay Debugger</h5>
      <ul className="nav nav-tabs mb-2">
        {[
          ["messages", "Messages"],
          ["chunks", "Chunks"],
          ["glossary", "Glossary"],
          ["score", "Score"],
        ].map(([key, label]) => (
          <li key={key} className="nav-item">
            <button
              className={`nav-link ${tab === key ? "active" : ""}`}
              onClick={() => setTab(key)}
            >
              {label}
            </button>
          </li>
        ))}
      </ul>
      {tab === "messages" && (
        <ol className="small">
          {frames.map((f, i) => (
            <li key={i}>{f.query}</li>
          ))}
        </ol>
      )}
      {tab === "chunks" && (
        <div>
          {frames.map((f, i) => (
            <div key={i} className="mb-3">
              <div className="fw-bold mb-1">{f.query}</div>
              <table className="table table-bordered table-sm">
                <thead className="table-light">
                  <tr>
                    <th>ID</th>
                    <th>Score</th>
                    <th>Anchors</th>
                  </tr>
                </thead>
                <tbody>
                  {f.chunks.map((c) => (
                    <tr key={c.chunk_id}>
                      <td className="text-muted small">{c.chunk_id}</td>
                      <td>{c.final_score?.toFixed(2)}</td>
                      <td>{(c.matched_anchors || []).join(", ")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}
      {tab === "glossary" && (
        <div>
          {frames.map((f, i) => (
            <div key={i} className="mb-2">
              <div className="fw-bold">{f.query}</div>
              <div>
                Hits:{" "}
                {f.glossary_hits.length > 0
                  ? f.glossary_hits.join(", ")
                  : "None"}
              </div>
              <div className="text-danger">
                Misses:{" "}
                {f.glossary_misses.length > 0
                  ? f.glossary_misses.join(", ")
                  : "None"}
              </div>
            </div>
          ))}
        </div>
      )}
      {tab === "score" && (
        <div>
          {frames.map((f, i) => (
            <div key={i} className="mb-2">
              <div className="fw-bold">{f.query}</div>
              <div className="small">
                Score: {f.retrieval_score?.toFixed(3)} | Fallback:{" "}
                {f.fallback ? "yes" : "no"}
              </div>
            </div>
          ))}
        </div>
      )}
      {data.reflection_summary && (
        <div className="mt-2 small text-muted">
          Reflection: {data.reflection_summary}
        </div>
      )}
    </div>
  );
}
