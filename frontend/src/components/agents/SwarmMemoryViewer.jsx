import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

const SwarmMemoryViewer = ({ tag }) => {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    apiFetch(`/agents/swarm-memory/?tag=${tag || ""}`)
      .then(setEntries)
      .catch((err) => console.error("Failed to load swarm memory", err));
  }, [tag]);

  return (
    <div>
      <h5>Swarm Memory</h5>
      <ul className="list-group">
        {entries.map((e) => (
          <li key={e.id} className="list-group-item">
            <strong>{e.title}</strong>
            <div>{e.content}</div>
          </li>
        ))}
        {entries.length === 0 && (
          <li className="list-group-item text-muted">No memory entries.</li>
        )}
      </ul>
    </div>
  );
};

export default SwarmMemoryViewer;

