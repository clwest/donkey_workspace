import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import DocumentIntelligencePanel from "../../components/intel/DocumentIntelligencePanel";
import DocumentAutoBuilder from "../../components/intel/DocumentAutoBuilder";
import ChunkDebugPanel from "../../components/intel/ChunkDebugPanel";
import "./styles/DocumentDetailPage.css";

export default function DocumentDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showSmartChunks, setShowSmartChunks] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(false);

  // Reset local state whenever the document id changes
  useEffect(() => {
    setDoc(null);
    setLoading(true);
    setShowSmartChunks(false);
    setSummaryLoading(false);
  }, [id]);

  useEffect(() => {
    async function fetchDoc() {
      try {
        const res = await apiFetch(`/intel/documents/${id}/`);
        setDoc(res);
      } catch (err) {
        console.error("Error fetching doc:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchDoc();
  }, [id]);

  const handleSummarize = async () => {
    setSummaryLoading(true);
    try {
      const url = showSmartChunks
        ? `/intel/documents/${id}/summarize_with_context/`
        : `/intel/intelligence/summarize/${id}/`;
      const options = showSmartChunks ? { method: "POST" } : {};
      const res = await apiFetch(url, options);
      setDoc((prev) => ({ ...prev, summary: res.summary }));
    } catch (err) {
      console.error("Summary error:", err);
    } finally {
      setSummaryLoading(false);
    }
  };

  if (loading) return <div className="container py-4">Loading...</div>;
  if (!doc) return <div className="container py-4">Document not found.</div>;

  const chunks = showSmartChunks ? doc.smart_chunks : doc.chunks;

  const assistants = doc.assistants || [];

  return (
    <div className="container py-4">
      <h2>📄 {doc.title}</h2>
      <p className="text-muted">
        Source: <a href={doc.source_url}>{doc.source_url}</a>
      </p>
      <p>
        <strong>Total Tokens:</strong> {doc.total_tokens}
      </p>
      <p className="mb-1">
        <strong>Chunks:</strong> {doc.num_chunks} | Embedded: {doc.num_embedded}
      </p>
      {assistants.length > 0 && (
        <p className="mb-2">
          <strong>Assigned Assistant:</strong>{" "}
          {assistants.map((a, i) => (
            <span key={a.id}>
              <Link to={`/assistants/${a.slug}/`}>{a.name}</Link>
              {i < assistants.length - 1 ? ", " : ""}
            </span>
          ))}
        </p>
      )}
      {doc.chunk_count === 0 && (
        <div className="alert alert-warning">
          This document has no visible chunks. Try re-ingesting or check the
          ingestion logs.
        </div>
      )}
      {doc.glossary_ids && doc.glossary_ids.length > 0 && (
        <p className="mb-1 small text-muted">
          Glossary IDs: {JSON.stringify(doc.glossary_ids)}
        </p>
      )}

      {doc.summary && (
        <div className="alert alert-info">
          <strong>🧠 Summary:</strong>
          <p className="mb-0">{doc.summary}</p>
        </div>
      )}

      <div className="my-3 d-flex gap-3">
        <button
          className="btn btn-outline-secondary"
          onClick={handleSummarize}
          disabled={summaryLoading}
        >
          {summaryLoading ? "Summarizing..." : "🧠 Summarize with Context"}
        </button>
      </div>
      <DocumentAutoBuilder docId={doc.id} />
      <ChunkDebugPanel docId={doc.id} />
      <div className="my-3 d-flex gap-3">
        <DocumentIntelligencePanel docId={doc.id} />
        {assistants.length > 0 && (
          <div className="d-flex align-items-center gap-2">
            <select
              id="reflectSelect"
              className="form-select"
              style={{ width: "auto" }}
            >
              {assistants.map((a) => (
                <option key={a.id} value={a.slug}>
                  {a.name}
                </option>
              ))}
            </select>
            <Link
              to={`/assistants/${assistants[0].slug}/review-ingest/${doc.id}/`}
              className="btn btn-sm btn-outline-secondary"
              onClick={(e) => {
                e.preventDefault();
                const slug = document.getElementById("reflectSelect").value;
                navigate(`/assistants/${slug}/review-ingest/${doc.id}/`);
              }}
            >
              Reflect with Assistant
            </Link>
          </div>
        )}
      </div>
      <div className="form-check form-switch my-3">
        <input
          className="form-check-input"
          type="checkbox"
          id="chunkToggle"
          checked={showSmartChunks}
          onChange={() => setShowSmartChunks(!showSmartChunks)}
        />
        <label className="form-check-label" htmlFor="chunkToggle">
          Toggle Smart Chunks
        </label>
      </div>
      <div className="mt-3">
        {chunks.map((chunk, i) => {
          const isGlossary =
            chunk.order === 0 && chunk.text.toLowerCase().includes("refers to");
          return (
            <div key={i} className="card mb-3">
              <div className="card-header">
                {isGlossary ? (
                  <>🔠 Glossary (auto-injected)</>
                ) : (
                  <>Chunk {chunk.order !== undefined ? chunk.order : i + 1}</>
                )}
                {" — "}
                {chunk.tokens} tokens | score {chunk.score?.toFixed(2)}
              </div>
              <div className="card-body">
                <p className="card-text">{chunk.text}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
