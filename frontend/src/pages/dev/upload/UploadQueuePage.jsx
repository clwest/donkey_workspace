import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import DocumentStatusCard from "../../../components/documents/DocumentStatusCard";

export default function UploadQueuePage() {
  const [uploads, setUploads] = useState([]);

  const load = async () => {
    try {
      const docs = await apiFetch("/intel/documents/?limit=100");
      const active = (docs || []).filter(
        (d) => d.progress_status !== "completed" && d.progress_status !== "failed"
      );
      setUploads(active);
    } catch (err) {
      console.error("Failed to load uploads", err);
    }
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 2000);
    return () => clearInterval(interval);
  }, []);

  const statusColor = (status) => {
    switch (status) {
      case "queued":
        return "secondary";
      case "embedding":
        return "warning";
      case "complete":
        return "success";
      case "failed":
        return "danger";
      default:
        return "info";
    }
  };

  return (
    <div className="container py-4">
      <h2>📤 Upload Queue</h2>
      <Link to="/intel/documents" className="btn btn-link mb-3">
        ← Back to Browser
      </Link>
      {uploads.length === 0 ? (
        <p className="text-muted">No active uploads.</p>
      ) : (
        <table className="table table-sm">
          <thead>
            <tr>
              <th>Title</th>
              <th>Assistant</th>
              <th>Tokens</th>
              <th>Chunks</th>
              <th>Status</th>
              <th>Updated</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {uploads.map((doc) => {
              const total = doc.chunk_count || doc.num_chunks || 0;
              const embedded = doc.embedded_chunks || doc.num_embedded || 0;
              return (
                <tr key={doc.id}>
                  <td>{doc.title || "Untitled"}</td>
                  <td>{doc.assistants?.[0]?.name || "-"}</td>
                  <td>{doc.token_count}</td>
                  <td>
                    {embedded}/{total}
                  </td>
                  <td>
                    <DocumentStatusCard doc={doc} />
                  </td>
                  <td>{doc.updated_at ? new Date(doc.updated_at).toLocaleString() : ""}</td>
                  <td>
                    <button
                      className="btn btn-sm btn-outline-danger me-1"
                      onClick={() => apiFetch(`/intel/documents/${doc.id}/retry/`, { method: "POST" }).then(load)}
                    >
                      🔁 Retry
                    </button>
                    <button
                      className="btn btn-sm btn-outline-info"
                      onClick={() => apiFetch(`/intel/documents/${doc.id}/force-embed/`, { method: "POST" }).then(load)}
                    >
                      🧠 Force Embed
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
