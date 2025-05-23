import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient"

export default function WorldTimelineAnchor() {
  const [data, setData] = useState({ memories: [], codices: [] });

  useEffect(() => {
    apiFetch("/agents/timeline/").then(setData).catch(() => setData({ memories: [], codices: [] }));
  }, []);

  return (
    <div className="container my-4">
      <h2>World Timeline</h2>
      <h5>Memories</h5>
      <ul>
        {data.memories.map((m) => (
          <li key={m.id}>{m.title}</li>
        ))}
      </ul>
      <h5>Codices</h5>
      <ul>
        {data.codices.map((c) => (
          <li key={c.id}>{c.title}</li>
        ))}
      </ul>
    </div>
  );
}
