import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ReformationRitualEditor() {
  const [rituals, setRituals] = useState([]);
  const [intent, setIntent] = useState("");

  useEffect(() => {
    apiFetch("/agents/memory-reformations/")
      .then(setRituals)
      .catch(() => setRituals([]));
  }, []);

  const submitRitual = async () => {
    if (!intent) return;
    const res = await apiFetch("/agents/memory-reformations/", {
      method: "POST",
      body: { symbolic_intent: intent },
    });
    setRituals([res, ...rituals]);
    setIntent("");
  };

  return (
    <div className="my-3">
      <h5>Memory Reformation Rituals</h5>
      <div className="input-group mb-2">
        <input
          type="text"
          className="form-control"
          placeholder="Symbolic intent"
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
        />
        <button className="btn btn-primary" onClick={submitRitual}>
          Start Ritual
        </button>
      </div>
      <ul className="list-group">
        {rituals.map((r) => (
          <li key={r.id} className="list-group-item">
            {r.symbolic_intent}
          </li>
        ))}
        {rituals.length === 0 && (
          <li className="list-group-item text-muted">No rituals recorded.</li>
        )}
      </ul>
    </div>
  );
}
