import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AssistantSuccessionTimeline({ assistantId }) {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    if (!assistantId) return;
    apiFetch(`/assistants/${assistantId}/succession/`)
      .then(setEntries)
      .catch(() => setEntries([]));
  }, [assistantId]);

  return (
    <div className="my-3">
      <h5>Succession Timeline</h5>
      <ul className="list-unstyled">
        {entries.map((e) => (
          <li key={e.id}>
            <strong>{e.predecessor.name}</strong> →
            <strong> {e.successor.name}</strong> ({e.reason})
          </li>
        ))}
      </ul>
    </div>
  );
}

