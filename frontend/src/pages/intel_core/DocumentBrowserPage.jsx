import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import DocumentCard from "../../components/intel/DocumentCard";
import DocumentIngestionForm from "../../components/intel/DocumentIngestionForm";
import { Badge } from "react-bootstrap";
import { Link } from "react-router-dom";

export default function DocumentBrowserPage() {
  const [groupedDocs, setGroupedDocs] = useState({});
  const [loading, setLoading] = useState(true);

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

    useEffect(() => {
      loadDocuments();
    }, []);

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
                  <DocumentCard group={group} />
                </Link>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}