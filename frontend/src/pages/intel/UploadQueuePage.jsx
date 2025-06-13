import { useState } from "react";
import { Link } from "react-router-dom";
import DocumentIngestionForm from "../../components/intel/DocumentIngestionForm";
import DocumentIngestingCard from "../../components/documents/DocumentIngestingCard";

export default function DocumentUploadQueuePage() {
  const [queue, setQueue] = useState([]);

  const handleQueued = (doc) => {
    setQueue((prev) => [doc, ...prev]);
  };

  return (
    <div className="container py-4">
      <h2>📤 Upload Queue</h2>
      <Link to="/intel/documents" className="btn btn-link mb-3">
        ← Back to Browser
      </Link>
      <DocumentIngestionForm onQueued={handleQueued} />
      {queue.length > 0 && (
        <div className="row mt-4">
          {queue.map((doc) => (
            <div key={doc.id} className="col-md-6 col-lg-4 mb-4">
              <DocumentIngestingCard doc={doc} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
