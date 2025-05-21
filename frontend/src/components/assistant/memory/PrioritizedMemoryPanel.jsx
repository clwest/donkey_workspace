import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";
import TagBadge from "../../TagBadge";

export default function PrioritizedMemoryPanel({ slug }) {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!slug) return;
    async function load() {
      try {
        const res = await apiFetch(
          `/assistants/${slug}/memories/prioritized/?task=reflection`
        );
        setMemories(res || []);
      } catch (err) {
        console.error("Failed to fetch prioritized memories", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  if (loading) return <div>Loading prioritized memories...</div>;
  if (memories.length === 0)
    return <div className="text-muted">No prioritized memories 🚫</div>;

  return (
    <div className="p-2 border rounded">
      <h5 className="mb-3">Prioritized Memories</h5>
      <ul className="list-group">
        {memories.map((m) => {
          const summary =
            m.summary || (m.event ? `${m.event.slice(0, 120)}…` : "(no content)");
          return (
            <li
              key={m.id}
              className="list-group-item d-flex justify-content-between align-items-start"
            >
              <div className="me-2">
                <div className="memory-summary">
                  <strong>{summary}</strong>
                </div>
                <div className="memory-meta small text-muted">
                  {new Date(m.created_at).toLocaleString()} • importance {m.importance}
                </div>
                {m.tags && m.tags.length > 0 && (
                  <div className="mt-1">
                    {m.tags.map((t) => (
                      <TagBadge key={t.id} tag={t} className="me-1" />
                    ))}
                  </div>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
