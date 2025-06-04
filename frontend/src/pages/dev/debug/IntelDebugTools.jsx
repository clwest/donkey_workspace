import { useEffect, useState } from "react";
import { Spinner } from "react-bootstrap";
import { toast } from "react-toastify";
import apiFetch from "../../../utils/apiClient";

export default function IntelDebugTools() {
  const [docs, setDocs] = useState([]);
  const [docId, setDocId] = useState("");
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [assistant, setAssistant] = useState("");
  const [results, setResults] = useState({});
  const [chunks, setChunks] = useState([]);

  useEffect(() => {
    async function loadDocs() {
      try {
        const res = await apiFetch(`/intel/documents/?limit=100`);
        setDocs(res.results || res);
      } catch (err) {
        console.error("Failed to load docs", err);
      } finally {
        setLoadingDocs(false);
      }
    }
    loadDocs();
  }, []);

  const loadChunks = async (id) => {
    try {
      const data = await apiFetch(`/intel/debug/chunks/${id}/`);
      setChunks(Array.isArray(data) ? data : data.chunks || data);
    } catch (err) {
      console.error("Chunk fetch failed", err);
    }
  };

  const run = async (name, options) => {
    setLoading(true);
    try {
      const data = await apiFetch(`/intel/debug/${name}/`, options);
      setResults((prev) => ({ ...prev, [name]: data }));
      toast.success(`✅ ${name} complete`);
      if (docId) await loadChunks(docId);
    } catch (err) {
      console.error(`${name} failed`, err);
      toast.error(`❌ ${name} failed`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-4">
      <h3>Intel Debug Tools</h3>
      <div className="mb-3">
        {loadingDocs ? (
          <Spinner animation="border" size="sm" />
        ) : (
          <select
            className="form-select w-auto"
            value={docId}
            onChange={(e) => setDocId(e.target.value)}
          >
            <option value="">Select document</option>
            {docs.map((d) => (
              <option key={d.id} value={d.id}>
                {d.title || d.slug}
              </option>
            ))}
          </select>
        )}
      </div>

      <details className="mb-3">
        <summary className="h5">Verify Embeddings</summary>
        <button
          className="btn btn-outline-primary mt-2"
          onClick={() =>
            run("verify-embeddings", { params: { document_id: docId } })
          }
          disabled={!docId || loading}
        >
          {loading ? <Spinner animation="border" size="sm" /> : "Run"}
        </button>
        {results["verify-embeddings"] && (
          <div className="mt-2 small">
            Mismatches: {results["verify-embeddings"].mismatches?.length || 0}
          </div>
        )}
      </details>

      <details className="mb-3">
        <summary className="h5">Fix Embeddings</summary>
        <button
          className="btn btn-outline-primary mt-2"
          onClick={() =>
            run("fix-embeddings", { method: "POST", body: { doc_id: docId } })
          }
          disabled={!docId || loading}
        >
          {loading ? <Spinner animation="border" size="sm" /> : "Run"}
        </button>
        {results["fix-embeddings"] && (
          <div className="mt-2 small">Updated: {results["fix-embeddings"].updated}</div>
        )}
      </details>

      <details className="mb-3">
        <summary className="h5">Recalculate Scores</summary>
        <button
          className="btn btn-outline-primary mt-2"
          onClick={() =>
            run("recalc-scores", { method: "POST", body: { document_id: docId } })
          }
          disabled={!docId || loading}
        >
          {loading ? <Spinner animation="border" size="sm" /> : "Run"}
        </button>
        {results["recalc-scores"] && (
          <div className="mt-2 small">Updated: {results["recalc-scores"].updated}</div>
        )}
      </details>

      <details className="mb-3">
        <summary className="h5">Repair Progress</summary>
        <button
          className="btn btn-outline-primary mt-2"
          onClick={() =>
            run("repair-progress", { method: "POST", body: { doc_id: docId } })
          }
          disabled={!docId || loading}
        >
          {loading ? <Spinner animation="border" size="sm" /> : "Run"}
        </button>
        {results["repair-progress"] && (
          <div className="mt-2 small">{results["repair-progress"].status}</div>
        )}
      </details>

      <details className="mb-3">
        <summary className="h5">Sync Chunk Counts</summary>
        <button
          className="btn btn-outline-primary mt-2"
          onClick={() => run("sync-chunk-counts", { method: "POST" })}
          disabled={loading}
        >
          {loading ? <Spinner animation="border" size="sm" /> : "Run"}
        </button>
        {results["sync-chunk-counts"] && (
          <pre className="mt-2 small">{results["sync-chunk-counts"].detail}</pre>
        )}
      </details>

      <details className="mb-3">
        <summary className="h5">RAG Recall</summary>
        <div className="mb-2">
          <input
            className="form-control mb-2"
            placeholder="Query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <input
            className="form-control mb-2"
            placeholder="Assistant ID or slug"
            value={assistant}
            onChange={(e) => setAssistant(e.target.value)}
          />
        </div>
        <button
          className="btn btn-outline-primary"
          onClick={() => run("rag-recall", { params: { query, assistant } })}
          disabled={!query || loading}
        >
          {loading ? <Spinner animation="border" size="sm" /> : "Run"}
        </button>
        {results["rag-recall"] && (
          <div className="mt-2 small">
            Results: {results["rag-recall"].results?.length || 0}
          </div>
        )}
      </details>

      {chunks.length > 0 && (
        <div className="mt-4">
          <h5>Chunk Inspection</h5>
          <table className="table table-sm table-bordered">
            <thead>
              <tr>
                <th>#</th>
                <th>Score</th>
                <th>Glossary</th>
                <th>Fingerprint</th>
              </tr>
            </thead>
            <tbody>
              {chunks.map((c) => (
                <tr
                  key={c.id}
                  className={
                    c.matched_anchors?.length > 0 &&
                    (c.glossary_score === 0 || !c.fingerprint)
                      ? "table-warning"
                      : ""
                  }
                >
                  <td>{c.order}</td>
                  <td>{c.score?.toFixed(2)}</td>
                  <td>{c.glossary_score?.toFixed(2)}</td>
                  <td>{c.fingerprint ? c.fingerprint.slice(0, 8) : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="small text-muted">
            Highlighted rows have glossary anchors missing scores or fingerprints
          </p>
        </div>
      )}
    </div>
  );
}
