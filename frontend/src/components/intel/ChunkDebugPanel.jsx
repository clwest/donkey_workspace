import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import { toast } from "react-toastify";

export default function ChunkDebugPanel({ docId }) {
  const [chunks, setChunks] = useState([]);
  const [showSkipped, setShowSkipped] = useState(false);
  const [isLoadingChunks, setIsLoadingChunks] = useState(true);
  const [reembedding, setReembedding] = useState(false);
  const [duplicateIds, setDuplicateIds] = useState(new Set());

  useEffect(() => {
    async function load() {
      setIsLoadingChunks(true);
      try {
        const params = showSkipped ? { skipped: "true" } : {};
        const res = await apiFetch(`/intel/documents/${docId}/chunks/`, { params });
        const list = Array.isArray(res) ? res : res.chunks || [];
        const seen = {};
        const dup = new Set();
        list.forEach((c) => {
          if (seen[c.order]) {
            dup.add(seen[c.order]);
            dup.add(c.id);
          } else {
            seen[c.order] = c.id;
          }
        });
        setDuplicateIds(dup);
        setChunks(list);
      } catch (err) {
        console.error("Failed to load chunks", err);
      } finally {
        setIsLoadingChunks(false);
      }
    }
    load();
  }, [docId, showSkipped]);

  const handleReembed = async (skipOnly) => {
    setReembedding(true);
    try {
      const res = await apiFetch(`/embeddings/reembed-skipped/`, {
        method: "POST",
        params: {
          document_id: docId,
          force: skipOnly ? undefined : "true",
          repair: "true",
        },
      });
      if (skipOnly) setShowSkipped(false);
      toast.success(`✅ Re-embedding started for ${res.reembedded} chunks`);
      const refreshed = await apiFetch(`/intel/documents/${docId}/chunks/`);
      const list = Array.isArray(refreshed) ? refreshed : refreshed.chunks || [];
      setChunks(list);
      const emb = list.filter((c) => c.embedding_id).length;
      toast.success(`Embedded ${emb} / ${list.length}`);
    } catch (err) {
      console.error("Reembed failed", err);
      toast.error("Re-embed failed");
    } finally {
      setReembedding(false);
    }
  };

  const handleRecalcScores = async () => {
    setReembedding(true);
    try {
      await apiFetch(`/intel/debug/recalc-scores/`, {
        method: "POST",
        body: { document_id: docId },
      });
      toast.success("Score recalculation queued");
    } catch (err) {
      console.error("Score recalc failed", err);
      toast.error("Score recalculation failed");
    } finally {
      setReembedding(false);
    }
  };

  const handleFixStatus = async () => {
    setReembedding(true);
    try {
      const res = await apiFetch(`/intel/debug/fix-embeddings/`, {
        method: "POST",
        body: { doc_id: docId },
      });
      toast.success(`Updated ${res.updated} chunk statuses`);
      const refreshed = await apiFetch(`/intel/documents/${docId}/chunks/`);
      const list = Array.isArray(refreshed) ? refreshed : refreshed.chunks || [];
      setChunks(list);
    } catch (err) {
      console.error("Status fix failed", err);
      toast.error("Status check failed");
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
      <div className="mb-2 d-flex gap-2">
        <button
          className="btn btn-sm btn-outline-primary"
          onClick={() => handleReembed(false)}
          disabled={reembedding || isLoadingChunks}
        >
          {reembedding ? "Re-embedding..." : "Re-embed All"}
        </button>
        <button
          className="btn btn-sm btn-outline-secondary"
          onClick={() => handleReembed(true)}
          disabled={reembedding || isLoadingChunks}
        >
          Re-embed Skipped
        </button>
        <button
          className="btn btn-sm btn-outline-warning"
          onClick={handleRecalcScores}
          disabled={reembedding || isLoadingChunks}
        >
          Recalculate Scores
        </button>
        <button
          className="btn btn-sm btn-outline-danger"
          onClick={handleFixStatus}
          disabled={reembedding || isLoadingChunks}
        >
          Re-verify Status
        </button>
      </div>
      {isLoadingChunks ? (
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
                <th title="Embedding ID. ⚠️ icon means status not 'embedded'">Embed ID</th>
              </tr>
            </thead>
            <tbody>
              {chunks.map((c, idx) => (
                <tr
                  key={c.id}
                  className={duplicateIds.has(c.id) ? "table-danger" : undefined}
                  title={
                    c.embedding_id
                      ? undefined
                      : "No embedding found. Use Re-embed All to fix."
                  }
                >
                  <td>{idx + 1}</td>
                  <td>{c.tokens}</td>
                  <td
                    title={
                      c.score < 0.3 && (!c.matched_anchors || c.matched_anchors.length === 0)
                        ? "Low score - no glossary hits"
                        : undefined
                    }
                  >
                    {c.score?.toFixed(2)}
                  </td>
                  <td>{c.skipped ? "❌" : ""}</td>
                  <td>{c.force_embed ? "⚠️" : ""}</td>
                  <td>
                    {c.embedding_id ? c.embedding_id.slice(0, 8) : "-"}
                    {c.embedding_status !== "embedded" && (
                      <span
                        className="ms-1 text-warning"
                        title={`Chunk status is '${c.embedding_status}' despite having an embedding`}
                      >
                        ⚠️
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
