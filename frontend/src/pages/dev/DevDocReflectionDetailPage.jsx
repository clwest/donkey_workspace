import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import TagBadge from "../../components/TagBadge";
import apiFetch from "../../utils/apiClient";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function DevDocReflectionDetailPage() {
  const { slug } = useParams();
  const [doc, setDoc] = useState(null);
  const [reflection, setReflection] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadReflectionDetail = async () => {
      try {
        const docRes = await apiFetch(`/mcp/dev_docs/${slug}/`);
        setDoc(docRes);

        const reflectRes = await apiFetch(`/mcp/dev_docs/${slug}/reflection/`);
        setReflection(reflectRes);
      } catch (err) {
        console.error("❌ Failed to load dev doc reflection detail:", err);
      } finally {
        setLoading(false);
      }
    };
    loadReflectionDetail();
  }, [slug]);

  if (loading) return <div className="container mt-4">Loading reflection...</div>;

  if (!doc || !reflection) {
    return (
      <div className="container mt-4">
        <h2>⚠️ Reflection Not Found</h2>
        <p>The reflection or document could not be found for <code>{slug}</code>.</p>
        <Link to="/dev-dashboard" className="btn btn-secondary mt-2">← Back to Dev Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <h2 className="mb-3">🧠 Reflection on: {doc.title}</h2>

      <div className="mb-4">
        <h4 className="text-muted">📄 Original Markdown</h4>
        <ReactMarkdown className="bg-light p-3 rounded border" remarkPlugins={[remarkGfm]}>
          {doc.content}
        </ReactMarkdown>
      </div>

      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">🪞 Reflection Summary</h5>
          <p><strong>{reflection.summary}</strong></p>

          <div className="mb-3">
            <h6 className="mb-1">Tags:</h6>
            {reflection.tags?.map((tag, idx) =>
              typeof tag === "string" ? (
                <span key={idx} className="badge bg-secondary me-1">
                  {tag}
                </span>
              ) : (
                <TagBadge key={tag.id || tag.slug || idx} tag={tag} />
              )
            )}
          </div>

          <pre className="bg-light p-2 rounded small overflow-auto">
            {reflection.event}
          </pre>

          <div className="text-muted small mt-2">
            🕒 {new Date(reflection.created_at).toLocaleString()}
          </div>
        </div>
      </div>

      <Link to="/dev-dashboard" className="btn btn-outline-secondary">← Back to Dev Dashboard</Link>
    </div>
  );
}
