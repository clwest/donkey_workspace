import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MemoryReprogrammingConsole() {
  const [scripts, setScripts] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/memory-reprogramming/");
        setScripts(res.results || res);
      } catch (err) {
        console.error("Failed to load scripts", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Memory Reprogramming Scripts</h5>
      <ul className="list-group">
        {scripts.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.trigger_condition} – {s.validation_result}
          </li>
        ))}
        {scripts.length === 0 && (
          <li className="list-group-item text-muted">No reprogramming scripts.</li>
        )}
      </ul>
    </div>
  );
}
