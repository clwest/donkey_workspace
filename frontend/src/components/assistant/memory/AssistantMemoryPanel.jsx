import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";
import ReflectNowButton from "../ReflectNowButton";
import TagBadge from "../../TagBadge";

export default function AssistantMemoryPanel({ slug }) {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!slug) return;
    async function load() {
      try {
        const res = await apiFetch(`/assistants/${slug}/memories/`);
        setMemories(res || []);
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
      {memories.length === 0 ? (
        <div className="text-muted">No memories found.</div>
      ) : (
        <ul className="list-group">
          {memories.map((m) => (
            <li key={m.id} className="list-group-item d-flex justify-content-between align-items-start">
              <div className="me-2">
                <div><strong>{m.summary || "(no summary)"}</strong></div>
                <div className="small text-muted">
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
          ))}
        </ul>
      )}
    </div>
  );
}
