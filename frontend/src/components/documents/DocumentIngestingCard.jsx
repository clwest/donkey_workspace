import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import DocumentStatusCard from "./DocumentStatusCard";
import apiFetch from "../../utils/apiClient";
export default function DocumentIngestingCard({ doc, highlightConflicts }) {
  const [localDoc, setLocalDoc] = useState(doc);

  useEffect(() => {
    setLocalDoc(doc);
  }, [doc]);

  useEffect(() => {
    const pid = doc?.metadata?.progress_id;
    if (!pid) return;
    let stop = false;

    const fetchProgress = async () => {
      try {
        const data = await apiFetch(`/intel/documents/${pid}/progress/`);
        setLocalDoc((prev) => ({
          ...prev,
          progress_status: data.status,
          progress_error: data.error_message,
          failed_chunks: data.failed_chunks,
          chunk_index: data.processed ?? prev.chunk_index,
          embedded_chunks: data.embedded_chunks ?? prev.embedded_chunks,
          num_embedded: data.embedded_chunks ?? prev.num_embedded,
          chunk_count: data.total_chunks ?? prev.chunk_count,
          num_chunks: data.total_chunks ?? prev.num_chunks,
        }));

        if (data.status === "completed" || data.status === "failed") {
          const full = await apiFetch(`/intel/documents/${doc.id}/`);
          if (!stop) setLocalDoc((prev) => ({ ...prev, ...full }));
          clearInterval(interval);
        }
      } catch (err) {
        console.error("Progress poll failed", err);
      }
    };

    fetchProgress();
    const interval = setInterval(fetchProgress, 3000);
    return () => {
      stop = true;
      clearInterval(interval);
    };
  }, [doc.id, doc?.metadata?.progress_id]);

  if (!localDoc) return null;

  const title = localDoc.title || "Untitled";
  const sourceType = localDoc.source_type || "";
  const embedded = localDoc.embedded_chunks ?? localDoc.num_embedded ?? 0;
  const created = localDoc.chunk_index ?? localDoc.chunk_count ?? 0;
  const total = localDoc.chunk_count ?? localDoc.num_chunks ?? created;
  const failedCount = localDoc.failed_chunks?.length || 0;
  const tokenCount = localDoc.token_count || 0;
  const progressPct = total ? Math.round((embedded / total) * 100) : 0;

  return (
    <div
      className={`card mb-3 shadow-sm p-3 ${
        highlightConflicts && failedCount > 0 ? "border-danger" : ""
      }`}
    >
      {localDoc.progress_status === "error" && (
        <div className="text-red-500 text-sm mt-2">
          ⚠️ Ingestion failed: {localDoc.progress_error || "Unknown error"}
        </div>
      )}
      <h5 className="mb-1">{title}</h5>
      <div className="small text-muted mb-2">Source: {sourceType}</div>
      <div className="small mb-1">
        <strong>Chunks:</strong>{" "}
        <span title={`${embedded}/${created} embedded/created`}>
          {embedded} / {created}
        </span>
        {created !== total && (
          <span className="ms-1" title={`Created ${created} of ${total}`}>
            ({created}/{total})
          </span>
        )}
        {failedCount > 0 && (
          <span className="ms-1 text-danger" title={`Failed chunks: ${localDoc.failed_chunks.join(", ")}`}>❌ {failedCount}</span>
        )}
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

        <DocumentStatusCard doc={localDoc} />
        {localDoc.prompt_id && localDoc.progress_status === "completed" && (
          <Link
            to={`/prompts/${localDoc.prompt_id}`}
            className="small text-decoration-underline"
          >
            📄 View Reflection Prompt

          </Link>
        )}
      </div>
    </div>
  );
}
