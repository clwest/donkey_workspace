import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DialogueScriptEditor() {
  const [scripts, setScripts] = useState([]);

  useEffect(() => {
    apiFetch("/simulation/dialogue-scripts/")
      .then((res) => setScripts(res.results || res))
      .catch(() => setScripts([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Dialogue Scripts</h5>
      <ul className="list-group">
        {scripts.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.title}
          </li>
        ))}
        {scripts.length === 0 && (
          <li className="list-group-item text-muted">No scripts.</li>
        )}
      </ul>
    </div>
  );
}
