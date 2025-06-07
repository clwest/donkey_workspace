import { useEffect, useState } from "react";
import { useParams, useLocation, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import useAuthGuard from "../../../hooks/useAuthGuard";

export default function RAGPlaybackPanel({ compareMode = false }) {
  useAuthGuard();
  const { slug, uuid } = useParams();
  const location = useLocation();
  const isCompare = compareMode || location.pathname.includes("/rag_playback/compare/");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const url = isCompare
      ? `/assistants/${slug}/rag_playback/compare/${uuid}/`
      : `/assistants/${slug}/rag_playback/${uuid}/`;
    apiFetch(url)
      .then((res) => setData(res))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [slug, uuid, isCompare]);

  if (loading) return <div className="container my-5">Loading...</div>;
  if (!data) return <div className="container my-5">Not found.</div>;

  return (
    <div className="container my-5">
      <h2 className="mb-3">RAG Playback</h2>
      <p>
        <strong>Query:</strong> {data.query}
      </p>
      <table className="table table-bordered table-sm">
        <thead className="table-light">
          <tr>
            <th>Chunk ID</th>
            <th>Raw</th>
            <th>Boost</th>
            <th>Final</th>
            <th>Anchors</th>
            <th>Fallback</th>
          </tr>
        </thead>
        <tbody>
          {(data.chunks || data.replay_chunks || []).map((c) => (
            <tr key={c.id} className={c.fallback_used ? "table-warning" : ""}>
              <td className="small text-muted">{c.id}</td>
              <td>{c.score?.toFixed(2)}</td>
              <td>{c.boost?.toFixed(2)}</td>
              <td>{c.final_score?.toFixed(2)}</td>
              <td>
                {(c.matched_anchors || []).map((a) => (
                  <span key={a} className="badge bg-info text-dark me-1">
                    {a}
                  </span>
                ))}
              </td>
              <td>{c.fallback_used ? "⚠️" : ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {data.original_chunks && (
        <div className="mt-4">
          <h5>Anchor Drift</h5>
          <table className="table table-sm">
            <thead>
              <tr>
                <th>Anchor</th>
                <th>Old</th>
                <th>New</th>
              </tr>
            </thead>
            <tbody>
              {data.anchor_drift.map((d, i) => (
                <tr key={i}>
                  <td>{d.label}</td>
                  <td>{d.old_score?.toFixed?.(2)}</td>
                  <td>{d.new_score?.toFixed?.(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Link to={`/assistants/${slug}/replays`} className="btn btn-secondary">
        Back to Replays
      </Link>
    </div>
  );
}
