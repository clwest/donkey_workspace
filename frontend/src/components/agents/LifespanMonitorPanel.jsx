import { useEffect, useState } from "react";
import { fetchLifespanModels } from "../../api/agents";

export default function LifespanMonitorPanel() {
  const [models, setModels] = useState([]);

  useEffect(() => {
    fetchLifespanModels().then(setModels).catch(() => setModels([]));
  }, []);

  if (models.length === 0) return <div>No lifespan models.</div>;

  return (
    <div className="card">
      <div className="card-header">Symbolic Lifespan Models</div>
      <ul className="list-group list-group-flush">
        {models.map((m) => (
          <li key={m.id} className="list-group-item">
            <strong>{m.assistant}</strong>
          </li>
        ))}
      </ul>
    </div>
  );
}
