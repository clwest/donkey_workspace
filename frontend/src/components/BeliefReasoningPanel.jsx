import { useState, useEffect } from "react";
import apiFetch from "../utils/apiClient";

export default function BeliefReasoningPanel({ assistantId }) {
  const [belief, setBelief] = useState(null);
  const [editingTone, setEditingTone] = useState("");

  useEffect(() => {
    async function load() {
      if (!assistantId) return;
      try {
        const data = await apiFetch(`/assistants/${assistantId}/`);
        setBelief(data.belief_vector || {});
        setEditingTone(data.belief_vector?.tone || "");
      } catch (err) {
        console.error("Failed to load belief vector", err);
      }
    }
    load();
  }, [assistantId]);

  if (!belief) return <div>Loading belief vector...</div>;

  return (
    <div className="p-3 border rounded bg-light">
      <h5>Belief Vector</h5>
      <pre className="small bg-white p-2 rounded">
        {JSON.stringify(belief, null, 2)}
      </pre>
      <div className="mt-2">
        <label className="form-label me-2">Tone:</label>
        <input
          type="text"
          className="form-control d-inline w-auto"
          value={editingTone}
          onChange={(e) => setEditingTone(e.target.value)}
        />
      </div>
    </div>
  );
}
