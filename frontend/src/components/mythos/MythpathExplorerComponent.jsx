import { useState, useEffect } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythpathExplorerComponent() {
  const [data, setData] = useState({ memories: [], codices: [], rituals: [] });
  const [mode, setMode] = useState("personal");

  useEffect(() => {
    apiFetch("/agents/timeline/explore/")
      .then(setData)
      .catch(() => setData({ memories: [], codices: [], rituals: [] }));
  }, []);

  return (
    <div className="my-3">
      <h5>Mythpath Explorer</h5>
      <select
        className="form-select mb-2"
        value={mode}
        onChange={(e) => setMode(e.target.value)}
      >
        <option value="personal">Personal</option>
        <option value="guild">Guild</option>
        <option value="swarm">Swarm</option>
      </select>
      <h6>Codices</h6>
      <ul>
        {data.codices.map((c) => (
          <li key={c.id}>{c.title}</li>
        ))}
      </ul>
      <h6>Memories</h6>
      <ul>
        {data.memories.map((m) => (
          <li key={m.id}>{m.title}</li>
        ))}
      </ul>
      <h6>Rituals</h6>
      <ul>
        {data.rituals.map((r) => (
          <li key={r.id}>{r.ritual_title}</li>
        ))}
      </ul>
    </div>
  );
}
