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
        <div className="row">
          {uploads.map((doc) => {
            const total = doc.chunk_count || doc.num_chunks || 0;
            const embedded = doc.embedded_chunks || doc.num_embedded || 0;
            const pct = total ? Math.round((embedded / total) * 100) : 0;
            return (
              <div key={doc.id} className="col-md-6 col-lg-4 mb-3">
                <div className="card p-3 shadow-sm">
                  <h5 className="mb-1">{doc.title || "Untitled"}</h5>
                  <div className="mb-2 small text-muted">{doc.source_type}</div>
                  <div className="progress mb-2" style={{ height: "6px" }}>
                    <div
                      className={`progress-bar bg-${statusColor(doc.progress_status)}`}
                      role="progressbar"
                      style={{ width: `${pct}%` }}
                      aria-valuenow={pct}
                      aria-valuemin="0"
                      aria-valuemax="100"
                    />
                  </div>
                  <div className="d-flex justify-content-between align-items-center">
                    <span className="small">
                      {embedded}/{total} chunks
                    </span>
                    <Link
                      to={`/intel/documents/${doc.id}`}
                      className="btn btn-sm btn-outline-secondary"
                    >
                      View Details
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
