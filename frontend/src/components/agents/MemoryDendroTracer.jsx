import { useEffect, useState } from "react";
import { fetchMemoryDendro } from "../../api/agents";

export default function MemoryDendroTracer() {
  const [marks, setMarks] = useState([]);

  useEffect(() => {
    fetchMemoryDendro().then(setMarks).catch(() => setMarks([]));
  }, []);

  if (marks.length === 0) return <div>No dendro marks.</div>;

  return (
    <div className="card">
      <div className="card-header">Memory Dendro Marks</div>
      <ul className="list-group list-group-flush">
        {marks.map((m) => (
          <li key={m.id} className="list-group-item">
            <strong>{m.dendro_layer}</strong> – {m.growth_direction}
          </li>
        ))}
      </ul>
    </div>
  );
}
