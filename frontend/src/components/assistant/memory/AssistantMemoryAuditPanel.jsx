import { useEffect, useState } from "react";
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
          <th># Chunks</th>
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
            <td>{d.total_chunks}</td>
            <td>{d.embedding_coverage}%</td>
            <td>{d.tags.join(", ")}</td>
            <td className="small">{d.last_chunk_summary}</td>
            <td>
              <a
                href={`/intel/documents/${d.document_id}`}
                className="btn btn-sm btn-outline-secondary me-1"
              >
                🔍
              </a>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
