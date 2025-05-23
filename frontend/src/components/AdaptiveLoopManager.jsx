import { useState } from "react";

export default function AdaptiveLoopManager({ assistantId, onTrigger }) {
  const [frequency, setFrequency] = useState(7);
  const handleSave = () => {
    fetch("http://localhost:8000/api/adaptive-loops/configs/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        assistant: assistantId,
        trigger_conditions: {},
        reflection_frequency_days: frequency,
        learning_targets: {},
      }),
    })
      .then((res) => res.json())
      .catch((e) => console.error("config", e));
  };
  const handleTrigger = () => {
    fetch(
      `http://localhost:8000/api/learning-loops/trigger/${assistantId}/`,
      { method: "POST" }
    )
      .then((res) => res.json())
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
