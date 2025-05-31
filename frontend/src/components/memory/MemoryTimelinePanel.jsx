import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MemoryTimelinePanel({
  assistantId,
  documentId,
  highlightId,
  initialEntries,
}) {
  const [entries, setEntries] = useState(initialEntries || []);

  useEffect(() => {
    if (initialEntries) return;
    if (!assistantId || !documentId) return;
    async function load() {
      try {
        const res = await apiFetch("/memory/list/", {
          params: { assistant_id: assistantId, document_id: documentId },
        });
        setEntries(res);
      } catch (err) {
        console.error("Failed to load memories", err);
        setEntries([]);
      }
    }
    load();
  }, [assistantId, documentId, initialEntries, highlightId]);

  return (
    <div className="mt-4">
      <h5>Memory Timeline</h5>
      <ul className="list-group">
        {entries.map((m) => (
          <li
            key={m.id}
            className={`list-group-item${
              highlightId === m.id ? " list-group-item-success" : ""
            }`}
          >
            <div className="fw-bold">
              {new Date(m.created_at).toLocaleString()}
            </div>
            <div>{m.title || m.summary || m.event}</div>
          </li>
        ))}
        {entries.length === 0 && (
          <li className="list-group-item text-muted">No memories found.</li>
        )}
      </ul>
    </div>
  );
}
