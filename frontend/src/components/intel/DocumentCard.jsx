import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import { countTokens } from "../../utils/tokenCount";
import { Badge } from "react-bootstrap";
import DocumentStatusCard from "../documents/DocumentStatusCard";
import { useState } from "react";
import { Star, StarFill } from "react-bootstrap-icons";

dayjs.extend(relativeTime);

const sourceColors = {
  url: "primary",
  pdf: "danger",
  youtube: "dark",
  video: "dark",
  markdown: "warning",
  text: "secondary",
};

export default function DocumentCard({ group, progress, onToggleFavorite, onDelete }) {
  if (!group) return null;

  // Allow the component to handle both a single Document object or
  // a grouped response from the `list_grouped_documents` API.
  const baseDoc = Array.isArray(group.documents) && group.documents.length > 0
    ? group.documents[0]
    : group;

  const mergedDoc = { ...baseDoc };
  if (progress) {
    if (progress.status) mergedDoc.progress_status = progress.status;
    if (progress.error_message) mergedDoc.progress_error = progress.error_message;
    if (Array.isArray(progress.failed_chunks)) mergedDoc.failed_chunks = progress.failed_chunks;
    if (typeof progress.embedded_chunks === "number") {
      mergedDoc.embedded_chunks = progress.embedded_chunks;
      mergedDoc.num_embedded = progress.embedded_chunks;
    }
    if (typeof progress.total_chunks === "number") {
      mergedDoc.chunk_count = progress.total_chunks;
      mergedDoc.num_chunks = progress.total_chunks;
    }
    mergedDoc.updated_at = new Date().toISOString();
  }

  const {
    id,
    title,
    source_url = group.source_url,
    source_type = group.source_type,
    created_at = group.latest_created,
    metadata,
    content,
    is_favorited = false,
  } = mergedDoc;

  const tokenCount =
    group.total_tokens ??
    mergedDoc.token_count ??
    metadata?.token_count ??
    (content ? countTokens(content) : 0);

  const chunkCount =
    mergedDoc.chunk_count ??
    mergedDoc.num_chunks ??
    metadata?.chunk_count ??
    0;

  const embeddedChunks =
    mergedDoc.embedded_chunks ??
    mergedDoc.num_embedded ??
    0;

  const inProgress = embeddedChunks > 0 && embeddedChunks < chunkCount;
  const progressPct = inProgress ? Math.round((embeddedChunks / chunkCount) * 100) : 0;

  const stuck =
    embeddedChunks === chunkCount &&
    chunkCount > 0 &&
    mergedDoc.progress_status &&
    mergedDoc.progress_status !== "completed";

  const updatedAt = mergedDoc.updated_at ?? group.updated_at ?? created_at;

  const isVideo = source_type === "youtube" || source_type === "video";
  const isURL = source_type === "url";
  const fileType = source_type ? source_type.toUpperCase() : "DOC";
  const badgeType = isVideo ? "VIDEO" : isURL ? "URL" : fileType;


  const domain = source_url
    ? new URL(source_url).hostname.replace("www.", "")
    : "No URL";

  const [favorite, setFavorite] = useState(is_favorited);

  const handleToggleFavorite = (e) => {
    e.preventDefault();
    const newFavorite = !favorite;
    setFavorite(newFavorite);
    if (onToggleFavorite) onToggleFavorite(id, newFavorite);
  };

  const handleDelete = (e) => {
    e.preventDefault();
    if (!onDelete) return;
    if (window.confirm("Delete this document?")) {
      onDelete(id);
    }
  };

  return (
    <div className="card mb-3 shadow-sm p-3 position-relative h-100">
      <div className="d-flex justify-content-between align-items-start">
        <div>
          <h5 className="mb-1">{title || "Untitled Document"}</h5>
          <small className="text-muted">
            {source_url ? (
              <span
                role="button"
                className="text-decoration-underline text-primary"
                onClick={(e) => {
                  e.stopPropagation();
                  window.open(source_url, "_blank", "noopener,noreferrer");
                }}
              >
                {domain}
              </span>
            ) : (
              domain
            )}
            {" • "}
            {dayjs(created_at).fromNow()}
          </small>
        </div>
        <div className="btn-group">
          <button
            onClick={handleToggleFavorite}
            className="btn btn-sm btn-outline-warning border-0"
            title={favorite ? "Unpin" : "Pin to favorites"}
          >
            {favorite ? <StarFill /> : <Star />}
          </button>
          {onDelete && (
            <button
              onClick={handleDelete}
              className="btn btn-sm btn-outline-danger border-0"
              title="Delete document"
            >
              🗑️
            </button>
          )}
        </div>
      </div>

      <div className="mt-2 text-muted small">
        <div>
          <strong>Chunks:</strong>{" "}
          <span
            className={
              embeddedChunks === 0
                ? "text-danger"
                : embeddedChunks < chunkCount
                ? "text-warning"
                : "text-success"
            }
            title={`${embeddedChunks} embedded, ${chunkCount - embeddedChunks} queued or skipped`}
          >
            {embeddedChunks} / {chunkCount} {inProgress && "(In Progress)"}
          </span>
          {inProgress && (
            <div className="progress mt-1" style={{ height: "4px" }}>
              <div
                className="progress-bar"
                role="progressbar"
                style={{ width: `${progressPct}%` }}
              />
            </div>
          )}
        </div>
        <div>
          <strong>Tokens:</strong> {tokenCount.toLocaleString()}
        </div>
        {updatedAt && (
          <div>
            <strong>Updated:</strong> {new Date(updatedAt).toLocaleString()}
          </div>
        )}
        <span className="me-2">
          <DocumentStatusCard doc={mergedDoc} />
        </span>
        {stuck && (
          <span className="text-warning" title="All chunks embedded but progress pending">
            ⚠️
          </span>
        )}
        <Badge bg={sourceColors[source_type] || "secondary"} className="ms-2">
          {badgeType}
        </Badge>
      </div>
    </div>
  );
}
