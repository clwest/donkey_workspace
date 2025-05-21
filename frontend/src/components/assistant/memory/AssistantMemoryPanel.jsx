import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";
import ReflectNowButton from "../ReflectNowButton";
import TagBadge from "../../TagBadge";

export default function AssistantMemoryPanel({ slug }) {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [project, setProject] = useState(null);

  useEffect(() => {
    if (!slug) return;
    async function load() {
      try {
        const [memRes, asst] = await Promise.all([
          apiFetch(`/assistants/${slug}/memories/`),
          apiFetch(`/assistants/${slug}/`),
        ]);
        console.log(memRes)
        console.log(asst)
        setMemories(memRes || []);
        setProject(asst.current_project || null);
      } catch (err) {
        console.error("Failed to fetch memories", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  if (loading) return <div>Loading memories...</div>;

  return (
    <div className="p-2 border rounded">
      <h5 className="mb-3">🧠 Recent Memories</h5>
      {project && (
        <div className="alert alert-secondary py-1 small">Project: {project.title}</div>
      )}
      {memories.length === 0 ? (
        <div className="text-muted">No recent memories 📭</div>
      ) : (
        <ul className="list-group">
          {memories.map((m) => {
            const summary =
              m.summary || (m.event ? `${m.event.slice(0, 120)}…` : "(no content)");

            return (
              <li
                key={m.id}
                className="list-group-item d-flex justify-content-between align-items-start shadow-sm p-3"
              >
                <div className="me-2">

                  <div className="memory-summary">
                    <strong>{summary}</strong>
                  </div>
                  <div className="memory-meta small text-muted">

                    {new Date(m.created_at).toLocaleString()} • {m.token_count} tokens
                  </div>
                  {m.tags && m.tags.length > 0 && (
                    <div className="mt-1">
                      {m.tags.map((t) => (
                        <TagBadge key={t.id} tag={t} className="me-1" />
                      ))}
                    </div>
                  )}
                </div>
                <ReflectNowButton slug={slug} memoryId={m.id} />
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
