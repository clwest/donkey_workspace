import { Link } from "react-router-dom";
import DocumentStatusCard from "./DocumentStatusCard";

export default function DocumentIngestingCard({ doc }) {
  if (!doc) return null;
  const title = doc.title || "Untitled";
  const sourceType = doc.source_type || "";
  const embedded = doc.embedded_chunks ?? doc.num_embedded ?? 0;
  const chunkIndex = doc.chunk_index ?? doc.chunk_count ?? 0;
  const tokenCount = doc.token_count || 0;
  const progressPct = chunkIndex ? Math.round((embedded / chunkIndex) * 100) : 0;

  return (
    <div className="card mb-3 shadow-sm p-3">
      <h5 className="mb-1">{title}</h5>
      <div className="small text-muted mb-2">Source: {sourceType}</div>
      <div className="small mb-1">
        <strong>Chunks:</strong> {embedded} / {chunkIndex}
      </div>
      <div className="small mb-1">
        <strong>Tokens:</strong> {tokenCount.toLocaleString()}
      </div>
      <div className="progress mb-2" style={{ height: "4px" }}>
        <div
          className="progress-bar progress-bar-striped progress-bar-animated"
          role="progressbar"
          style={{ width: `${progressPct}%` }}
        />
      </div>
      <div className="d-flex align-items-center gap-2">
        <DocumentStatusCard doc={doc} />
        {doc.reflection_prompt_id && doc.progress_status === "completed" && (
          <Link
            to={`/prompts/${doc.reflection_prompt_id}`}
            className="small text-decoration-underline"
          >
            📄 {doc.reflection_prompt_title || "View Reflection Prompt"}
          </Link>
        )}
      </div>
    </div>
  );
}
