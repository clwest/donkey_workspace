import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function NarrativeAutonomyPanel() {
  const [models, setModels] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/assistants/autonomy-models/");
        setModels(res.results || res);
      } catch (err) {
        console.error("Failed to load autonomy models", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Narrative Autonomy</h5>
      <ul className="list-group">
        {models.map((m) => (
          <li key={m.id} className="list-group-item">
            <strong>{m.assistant_name || m.assistant}</strong> – {m.current_arc}
          </li>
        ))}
        {models.length === 0 && (
          <li className="list-group-item text-muted">No autonomy data.</li>
        )}
      </ul>
    </div>
  );
}
