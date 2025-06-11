import { Badge, OverlayTrigger, Tooltip } from "react-bootstrap";

export default function DocumentStatusCard({ doc }) {
  if (!doc) return null;

  const chunkCount = doc.chunk_count ?? doc.num_chunks ?? 0;
  const embedded = doc.num_embedded ?? doc.embedded_chunks ?? 0;
  const progressStatus = doc.progress_status || doc.embedding_status?.status;

  const failed = progressStatus === "failed" || progressStatus === "error";
  const completed = progressStatus === "completed";
  const inProgress = !completed && !failed;

  let color = "secondary";
  let label = "";
  let icon = "";
  let tip = "";

  if (failed) {
    color = "danger";
    icon = "⚠️";
    label = progressStatus === "error" ? "Error" : "Failed";
    const reasons = [];
    if (doc.progress_error) reasons.push(doc.progress_error);
    if (Array.isArray(doc.failed_chunks) && doc.failed_chunks.length > 0) {
      reasons.push(`Failed chunks: ${doc.failed_chunks.join(", ")}`);
    } else {
      reasons.push("No failed chunks");
    }
    tip = reasons.join("; ") || "Upload failed";
  } else if (completed) {
    color = "success";
    icon = "✅";
    label = "Completed";
    tip = "Document embedding complete";
  } else if (inProgress) {
    color = "warning";
    icon = "⏳";
    if (chunkCount > 0) {
      label = `Embedding Chunks: ${embedded}/${chunkCount}`;
    } else {
      label = "Uploading...";
    }
    if (Array.isArray(doc.failed_chunks) && doc.failed_chunks.length > 0) {
      tip = `Failed chunks: ${doc.failed_chunks.join(", ")}`;
    } else if (doc.updated_at) {
      tip = `Last updated: ${new Date(doc.updated_at).toLocaleString()}`;
    } else {
      tip = "No failed chunks";
    }
  }

  const badge = (
    <Badge bg={color} className="status-badge">
      {icon} {label}
    </Badge>
  );

  return tip ? (
    <OverlayTrigger overlay={<Tooltip>{tip}</Tooltip>}>{badge}</OverlayTrigger>
  ) : (
    badge
  );
}
