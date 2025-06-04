import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Badge, OverlayTrigger, Tooltip } from "react-bootstrap";
import apiFetch from "../../../utils/apiClient";

export default function AssistantMemoryAuditPanel({ assistant }) {
  const [docs, setDocs] = useState(null);

  useEffect(() => {
    if (!assistant) return;
    async function load() {
      try {
        const res = await apiFetch(`/assistants/${assistant.slug}/memory-documents/`);
        setDocs(res || []);
      } catch (err) {
        console.error("Failed to load memory docs", err);
      }
    }
    load();
  }, [assistant]);

  if (!docs) return <div>Loading...</div>;
  if (docs.length === 0) return <div>No linked documents.</div>;

  return (
    <table className="table table-sm">
      <thead>
        <tr>
          <th>Document Title</th>
          <th>Chunks Embedded</th>
          <th>% Embedded</th>
          <th>Tags</th>
          <th>Last Summary</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {docs.map((d) => (
          <tr key={d.document_id}>
            <td>{d.title}</td>
            <td>
              {d.embedded_chunks}/{d.total_chunks}
            </td>
            <td>
              {(() => {
                const embedded = d.embedded_chunks ?? 0;
                const total = d.total_chunks ?? 0;
                const pct = total
                  ? Math.min(100, Math.round((embedded / total) * 100))
                  : 0;
                return (
                  <>
                    {pct}%
                    {embedded > total && (
                      <Badge
                        bg="danger"
                        className="ms-1"
                        title="Mismatch: More embedded than total. Run sync_chunk_counts."
                      >
                        ⚠️
                      </Badge>
                    )}
                  </>
                );
              })()}
            </td>
            <td>{d.tags && d.tags.length > 0 ? d.tags.join(", ") : "—"}</td>
            <td className="small">{d.last_chunk_summary}</td>
            <td>
              <Link
                to={`/intel/documents/${d.document_id}`}
                className="btn btn-sm btn-outline-secondary me-1"
              >
                🔍
              </Link>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
