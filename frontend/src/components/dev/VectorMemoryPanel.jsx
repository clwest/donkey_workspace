import React from "react";
import { useRecentVectorMemories } from "../../hooks/useRecentVectorMemories";

export default function VectorMemoryPanel() {
  const { memories, loading } = useRecentVectorMemories();

  if (loading) return <div>Loading vector memories...</div>;

  return (
    <div className="p-3 border rounded bg-light">
      <h5 className="mb-3">🧠 Recent Vector Queries</h5>
      {memories.length === 0 ? (
        <div>No vector-based memories found.</div>
      ) : (
        <ul className="list-group">
          {memories.map((memory, i) => {
            console.log("🧠 Vector Memory Entry:", memory);
            return (
              <li key={memory.id || i} className="list-group-item mb-2">
                <div><strong>{memory.summary || memory.event.slice(0, 80)}...</strong></div>
                <div className="text-muted small">{new Date(memory.created_at).toLocaleString()}</div>

                {memory.tags?.length > 0 && (
                  <div className="mt-1">
                    {memory.tags.map((tag, j) => (
                            <span
                              key={tag.id}
                              className="badge bg-secondary me-1"
                              title={tag.slug}
                              style={{ backgroundColor: tag.color || undefined }}
                            >
                        {tag.name}
                      </span>
                    ))}
                  </div>
                )}

                {memory.linked_object_id && memory.linked_content_type && (
                  <div className="mt-1">
                    <em>🔗 Linked: {memory.linked_content_type.model} (ID: {memory.linked_object_id})</em>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}