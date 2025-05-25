import { useState } from "react";
import apiFetch from "../utils/apiClient";

export default function AdaptiveLoopManager({ assistantId, onTrigger }) {
  const [frequency, setFrequency] = useState(7);
  const handleSave = () => {
    apiFetch(`/adaptive-loops/configs/`, {
      method: "POST",
      body: {
        assistant: assistantId,
        trigger_conditions: {},
        reflection_frequency_days: frequency,
        learning_targets: {},
      },
    })
      .then((res) => res)
      .catch((e) => console.error("config", e));
  };
  const handleTrigger = () => {
    apiFetch(`/learning-loops/trigger/${assistantId}/`, { method: "POST" })
      .then((res) => res)
      .then((data) => onTrigger && onTrigger(data))
      .catch((e) => console.error("trigger", e));
  };

  return (
    <div className="p-2 border rounded">
      <h5>Adaptive Loop</h5>
      <button className="btn btn-secondary" onClick={handleTrigger}>
        Trigger Now
      </button>
      <div className="mt-2">
        <input
          type="number"
          className="form-control mb-1"
          value={frequency}
          onChange={(e) => setFrequency(e.target.value)}
        />
        <button className="btn btn-primary" onClick={handleSave}>
          Save Config
        </button>
      </div>
    </div>
  );
}
