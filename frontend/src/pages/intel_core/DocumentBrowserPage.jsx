import { useEffect, useState, useRef } from "react";
import apiFetch, { API_URL } from "../../utils/apiClient";
import DocumentCard from "../../components/intel/DocumentCard";
import DocumentIngestionForm from "../../components/intel/DocumentIngestionForm";
import DocumentIngestingCard from "../../components/documents/DocumentIngestingCard";
import { Badge } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

export default function DocumentBrowserPage() {
  const navigate = useNavigate();
  const [groupedDocs, setGroupedDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [progressMap, setProgressMap] = useState({});
  const [ingestingDocs, setIngestingDocs] = useState([]);
  const prevIngestCount = useRef(0);
  const [highlightConflicts, setHighlightConflicts] = useState(false);
  const handleQueued = () => {
    toast.success("✓ Document queued for ingestion");
  };

  const loadDocuments = async () => {
    try {
      const res = await apiFetch("/intel/documents/grouped/");
      console.log("Grouped response", res);
      setGroupedDocs(res || []);
    } catch (err) {
      console.error("Failed to load grouped documents", err);
    } finally {
      setLoading(false);
    }
  };

  const pollProgress = async () => {
    const updates = {};
    for (const group of groupedDocs) {
      if (!group.documents) continue;
      for (const doc of group.documents) {
        const pid = doc.metadata?.progress_id;
        if (pid && doc.progress_status !== "completed" && doc.progress_status !== "failed") {
          try {
            const data = await apiFetch(`/intel/documents/${pid}/progress/`);
            updates[doc.id] = data;
          } catch (err) {
            console.error("Progress poll failed", err);
          }
        }
      }
    }
    if (Object.keys(updates).length > 0) {
      setProgressMap((prev) => ({ ...prev, ...updates }));
    }
  };

  const loadIngestingDocs = async () => {
    try {
      const data = await apiFetch("/intel/documents/", { params: { limit: 50 } });
      const inProgress = (data || []).filter(
        (d) => d.progress_status === "in_progress"
      );
      if (prevIngestCount.current > 0 && inProgress.length === 0) {
        loadDocuments();
      }
      prevIngestCount.current = inProgress.length;
      setIngestingDocs(inProgress);
    } catch (err) {
      console.error("Failed to load ingesting docs", err);
    }
  };

  const handleDeleteDocument = async (docId) => {
    if (!window.confirm("Delete this document?")) return;
    try {
      await apiFetch(`/intel/documents/${docId}/`, { method: "DELETE" });
      await loadDocuments();
    } catch (err) {
      console.error("Failed to delete document", err);
      alert("Failed to delete document");
    }
  };

  useEffect(() => {
    loadDocuments();
    loadIngestingDocs();
  }, []);

  useEffect(() => {
    const interval = setInterval(pollProgress, 3000);
    return () => clearInterval(interval);
  }, [groupedDocs]);

  useEffect(() => {
    const interval = setInterval(loadIngestingDocs, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container py-4">
      <h2>🧾 Document Browser</h2>
      <div className="d-flex justify-content-end mb-2 gap-2">
        <button
          className="btn btn-secondary"
          onClick={() => navigate('/intel/upload/queue')}
        >
          📤 Upload Batch
        </button>
        <button
          className="btn btn-primary"
          onClick={() => navigate('/dev/upload/queue')}
        >
          View Upload Queue
        </button>
      </div>

      <div className="form-check form-switch mb-3">
        <input
          className="form-check-input"
          type="checkbox"
          id="highlightConflictsToggle"
          checked={highlightConflicts}
          onChange={() => setHighlightConflicts(!highlightConflicts)}
        />
        <label className="form-check-label" htmlFor="highlightConflictsToggle">
          Highlight Symbolic Conflicts
        </label>
      </div>

      <DocumentIngestionForm
        onSuccess={() => {
          loadDocuments();
          loadIngestingDocs();
        }}
        onQueued={handleQueued}
      />

      {ingestingDocs.length > 0 && (
        <div className="row mt-4">
          {ingestingDocs.map((doc) => (
            <div key={doc.id} className="col-md-6 col-lg-4 mb-4">
              <DocumentIngestingCard doc={doc} highlightConflicts={highlightConflicts} />
            </div>
          ))}
        </div>
      )}

      {loading ? (
        <p className="text-muted mt-3">Loading documents...</p>
      ) : !Array.isArray(groupedDocs) || groupedDocs.length === 0 ? (
        <p className="text-muted mt-3">No documents found.</p>
      ) : (
        <div className="row mt-4">
          {groupedDocs.map((group, index) => {
            const { title, source_type, documents } = group;
            if (!documents || documents.length === 0) return null;

            const firstDoc = documents[0];

            return (
              <div className="col-md-6 col-lg-4 mb-4" key={index}>
                <Link
                  to={`/intel/documents/${firstDoc.id}`}
                  className="text-decoration-none"
                >
                  <DocumentCard
                    group={group}
                    progress={progressMap[firstDoc.id]}
                    onDelete={() => handleDeleteDocument(firstDoc.id)}
                  />
                </Link>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}