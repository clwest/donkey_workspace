import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ChunkDebugPanel({ docId }) {
  const [chunks, setChunks] = useState([]);
  const [showSkipped, setShowSkipped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [reembedding, setReembedding] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const params = showSkipped ? { skipped: "true" } : {};
        const res = await apiFetch(`/intel/documents/${docId}/chunks/`, { params });
        setChunks(res);
      } catch (err) {
        console.error("Failed to load chunks", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [docId, showSkipped]);

  const handleReembed = async () => {
    setReembedding(true);
    try {
      await apiFetch(`/embeddings/reembed-skipped/`, {
        method: "POST",
        params: { document_id: docId },
      });
      setShowSkipped(false);
    } catch (err) {
      console.error("Reembed failed", err);
    } finally {
      setReembedding(false);
    }
  };

  const total = chunks.length;
  const embedded = chunks.filter((c) => c.embedding_id).length;
  const skipped = chunks.filter((c) => c.skipped).length;
  const avgScore = total ? (chunks.reduce((a, c) => a + (c.score || 0), 0) / total).toFixed(2) : "0";

  return (
    <div className="mb-4">
      <div className="d-flex justify-content-between align-items-center mb-2">
        <h5>🩺 Chunk Debug Panel</h5>
        <div className="form-check form-switch">
          <input
            className="form-check-input"
            type="checkbox"
            id="showSkippedToggle"
            checked={showSkipped}
            onChange={() => setShowSkipped(!showSkipped)}
          />
          <label className="form-check-label" htmlFor="showSkippedToggle">
            Show Skipped Chunks
          </label>
        </div>
      </div>
      <p className="mb-2 small">
        Total: {total} | Embedded: {embedded} | Skipped: {skipped} | Avg score: {avgScore}
      </p>
      <button className="btn btn-sm btn-outline-primary mb-2" onClick={handleReembed} disabled={reembedding}>
        {reembedding ? "Re-embedding..." : "Re-embed Skipped Chunks"}
      </button>
      {loading ? (
        <div>Loading chunks...</div>
      ) : (
        <div className="table-responsive">
          <table className="table table-sm table-bordered">
            <thead>
              <tr>
                <th>#</th>
                <th>Tokens</th>
                <th>Score</th>
                <th>Skipped</th>
                <th>Force</th>
                <th>Embed ID</th>
              </tr>
            </thead>
            <tbody>
              {chunks.map((c) => (
                <tr key={c.id}>
                  <td>{c.order}</td>
                  <td>{c.token_count}</td>
                  <td>{c.score?.toFixed(2)}</td>
                  <td>{c.skipped ? "❌" : ""}</td>
                  <td>{c.force_embed ? "⚠️" : ""}</td>
                  <td>{c.embedding_id ? c.embedding_id.slice(0, 8) : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
