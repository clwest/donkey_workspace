import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import useAuditEmbeddingLinks from "../../../hooks/useAuditEmbeddingLinks";
import ErrorCard from "../../../components/ErrorCard";

export default function EmbeddingDebug() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [showRag, setShowRag] = useState(false);
  const [assistant, setAssistant] = useState("");
  const { rows: auditRows, reload } = useAuditEmbeddingLinks();

  const doRepair = async (id) => {
    await apiFetch(`/dev/embedding-audit/${id}/repair/`, { method: "PATCH" });
    reload();
  };

  const doIgnore = async (id) => {
    await apiFetch(`/dev/embedding-audit/${id}/ignore/`, { method: "PATCH" });
    reload();
  };

  useEffect(() => {
    async function load() {
      try {
        let url = showRag ? "/dev/embedding-debug/?include_rag=1" : "/dev/embedding-debug/";
        if (assistant) {
          const prefix = url.includes("?") ? "&" : "?";
          url += `${prefix}assistant=${assistant}`;
        }
        const res = await apiFetch(url);
        setData(res);
      } catch (err) {
        console.error("Failed to load embedding stats", err);
        setError(err);
      }
    }
    load();
  }, [showRag, assistant]);

  if (error?.status === 403) {
    return <ErrorCard message="You don't have permission to view embedding diagnostics." />;
  }

  if (!data && !error) {
    return <div className="container py-4">Loading...</div>;
  }

  return (
    <div className="container py-4">
      <h3>Embedding Debug</h3>
      <div className="input-group mb-3" style={{ maxWidth: "300px" }}>
        <input
          type="text"
          className="form-control"
          placeholder="Assistant slug or id"
          value={assistant}
          onChange={(e) => setAssistant(e.target.value)}
        />
      </div>
      <h5 className="mt-3">Model Counts</h5>
      <table className="table table-sm w-auto">
        <thead>
          <tr>
            <th>Model</th>
            <th>Count</th>
          </tr>
        </thead>
        <tbody>
          {data.model_counts.map((row) => (
            <tr key={row.model_used || "unknown"}>
              <td>{row.model_used || "Unknown"}</td>
              <td>{row.count}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-4">
        <strong>Embeddings with invalid links: {data.invalid_links}</strong>
      </div>
      {data.orphan_embeddings && data.orphan_embeddings.length > 0 && (
        <div className="mt-2 text-warning">
          Orphan embeddings: {data.orphan_embeddings.length}
        </div>
      )}
      {data.assistants_no_docs && data.assistants_no_docs.length > 0 && (
        <div className="mt-2 text-danger">
          Assistants without documents: {data.assistants_no_docs.join(", ")}
        </div>
      )}
      {auditRows && (
        <>
          <h5 className="mt-4">Mismatched Embeddings</h5>
          <table className="table table-sm">
            <thead>
              <tr>
                <th>Assistant</th>
                <th>Context ID</th>
                <th>Count</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {auditRows.map((row) => (
                <tr key={row.context_id}>
                  <td>
                    <Link to={`/assistants/${row.assistant}/memory/${row.context_id}/`}>
                      {row.assistant_name}
                    </Link>
                  </td>
                  <td>{row.context_id}</td>
                  <td>{row.count}</td>
                  <td>
                    <span
                      className={`badge ${row.status === 'pending' ? 'bg-warning' : row.status === 'repaired' ? 'bg-success' : 'bg-secondary'}`}
                    >
                      {row.status}
                    </span>
                  </td>
                  <td>
                    {row.status === 'pending' && (
                      <>
                        <button className="btn btn-sm btn-primary me-2" onClick={() => doRepair(row.context_id)}>
                          Fix
                        </button>
                        <button className="btn btn-sm btn-outline-secondary" onClick={() => doIgnore(row.context_id)}>
                          Ignore
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
      <div className="form-check form-switch mt-4">
        <input
          className="form-check-input"
          type="checkbox"
          id="ragToggle"
          checked={showRag}
          onChange={(e) => setShowRag(e.target.checked)}
        />
        <label className="form-check-label" htmlFor="ragToggle">
          Show Retrieval Stats
        </label>
      </div>
      {showRag && data.context_stats && (
        <div className="mt-3">
          <h5>Context Retrieval Counts</h5>
          <table className="table table-sm">
            <thead>
              <tr>
                <th>Assistant</th>
                <th>Context ID</th>
                <th>Chunks</th>
              </tr>
            </thead>
            <tbody>
              {data.context_stats.map((row, idx) => (
                <tr key={idx}>
                  <td>{row.assistant}</td>
                  <td>{row.context_id}</td>
                  <td>{row.chunk_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {data.retrieval_checks && (
            <table className="table table-sm mt-3">
              <thead>
                <tr>
                  <th>Assistant</th>
                  <th>Documents (all)</th>
                  <th>Retrieved</th>
                </tr>
              </thead>
              <tbody>
                {data.retrieval_checks.map((row, idx) => (
                  <tr key={idx}>
                    <td>{row.assistant}</td>
                    <td>{row.documents}</td>
                    <td className={row.documents > 0 && row.retrieved === 0 ? "text-danger" : ""}>{row.retrieved}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
      {data.orphaned_embeddings && data.orphaned_embeddings.length > 0 && (
        <div className="mt-4">
          <h5>Orphaned Embeddings</h5>
          <pre className="bg-light p-2" style={{ maxHeight: "200px", overflowY: "auto" }}>
            {JSON.stringify(data.orphaned_embeddings, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
