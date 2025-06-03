import { Badge, OverlayTrigger, Tooltip } from "react-bootstrap";

export default function DocumentStatusCard({ doc }) {
  if (!doc) return null;

  const chunkCount = doc.chunk_count ?? doc.num_chunks ?? 0;
  const embedded = doc.num_embedded ?? doc.embedded_chunks ?? 0;
  const progressStatus = doc.progress_status || doc.embedding_status?.status;

  const failed = progressStatus === "failed" || chunkCount === 0;
  const inProgress = embedded < chunkCount && !failed;

  let color = "success";
  let label = "Healthy";
  let tip = "Document embedding complete";

  if (failed) {
    color = "danger";
    label = "Broken";
    tip = "Document failed to embed. Repair suggested.";
  } else if (inProgress) {
    color = "warning";
    label = "Incomplete";
    tip = "Embedding in progress";
  }

  return (
    <OverlayTrigger overlay={<Tooltip>{tip}</Tooltip>}>
      <Badge bg={color}>{label}</Badge>
    </OverlayTrigger>
  );
}
