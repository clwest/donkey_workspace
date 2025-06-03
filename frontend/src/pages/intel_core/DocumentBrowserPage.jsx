import { useEffect, useState } from "react";
import apiFetch, { API_URL } from "../../utils/apiClient";
import DocumentCard from "../../components/intel/DocumentCard";
import DocumentIngestionForm from "../../components/intel/DocumentIngestionForm";
import { Badge } from "react-bootstrap";
import { Link } from "react-router-dom";

export default function DocumentBrowserPage() {
  const [groupedDocs, setGroupedDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [progressMap, setProgressMap] = useState({});

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

  const handleDeleteDocument = async (docId) => {
    if (!window.confirm("Delete this document?")) return;
    try {
      const res = await fetch(`${API_URL}/intel/documents/${docId}/`, {
        method: "DELETE",
        credentials: "include",
      });
      if (!res.ok) throw new Error("Delete failed");
      await loadDocuments();
    } catch (err) {
      console.error("Failed to delete document", err);
      alert("Failed to delete document");
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    const interval = setInterval(pollProgress, 3000);
    return () => clearInterval(interval);
  }, [groupedDocs]);

  return (
    <div className="container py-4">
      <h2>🧾 Document Browser</h2>

      <DocumentIngestionForm onSuccess={loadDocuments} />

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