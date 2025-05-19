import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import TagBadge from "../../../components/TagBadge";

export default function AssistantReflectionDetailPage() {
  const { id } = useParams();
  const [reflection, setReflection] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch(`/assistants/reflections/${id}/`);
        setReflection(data);
      } catch (err) {
        console.error("Failed to load reflection", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) return <div className="container my-5">Loading...</div>;
  if (!reflection) return <div className="container my-5">Not found.</div>;

  return (
    <div className="container my-5">
      <h2 className="mb-3">Reflection Detail</h2>
      <div className="mb-2 text-muted">
        {new Date(reflection.created_at).toLocaleString()}
      </div>
      {reflection.tags && (
        <div className="mb-3">
          {reflection.tags.map((t) => (
            <TagBadge key={t.id} tag={t} className="me-1" />
          ))}
        </div>
      )}
      <h5>Summary</h5>
      <p>{reflection.summary}</p>
      <h5>Raw Prompt</h5>
      <pre className="bg-light p-2 rounded">{reflection.raw_prompt || "-"}</pre>
      <h5>LLM Response</h5>
      <ReactMarkdown remarkPlugins={[remarkGfm]} className="markdown">
        {reflection.llm_summary || "-"}
      </ReactMarkdown>
      {reflection.linked_memory && (
        <div className="mt-4">
          <h5>Linked Memory</h5>
          <pre className="bg-light p-2 rounded">
            {reflection.linked_memory.event || reflection.linked_memory.summary}
          </pre>
        </div>
      )}
      <Link to={-1} className="btn btn-outline-secondary mt-4">
        Back
      </Link>
    </div>
  );
}
