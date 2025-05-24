import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient"

export default function WorldTimelineAnchor() {
  const [data, setData] = useState({ memories: [], codices: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch the combined memory + codex timeline. If the
    // endpoint changes shape or fails, fall back to empty
    // arrays so the component doesn't crash.
    apiFetch("/memory/timeline/")
      .then((resp) => {
        // some older endpoints returned just an array. Ensure
        // we always store an object with memories and codices
        if (Array.isArray(resp)) {
          setData({ memories: resp, codices: [] });
        } else {
          const memories = resp.memories || [];
          const codices = resp.codices || [];
          setData({ memories, codices });
        }
      })
      .catch(() => setData({ memories: [], codices: [] }))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="container my-4">
      <h2>World Timeline</h2>
      {loading && <div>Loading timeline...</div>}
      <h5>Memories</h5>
      <ul>
        {(data.memories || []).map((m) => (
          <li key={m.id}>{m.title}</li>
        ))}
      </ul>
      <h5>Codices</h5>
      <ul>
        {(data.codices || []).map((c) => (
          <li key={c.id}>{c.title}</li>
        ))}
      </ul>
    </div>
  );
}
