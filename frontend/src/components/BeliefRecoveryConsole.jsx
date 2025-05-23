import { useState } from "react";
import apiFetch from "../utils/apiClient";

export default function BeliefRecoveryConsole({ assistantId, memoryId }) {
  const [collapseType, setCollapseType] = useState("");
  const handleRun = () => {
    apiFetch("/belief-recovery/", {
      method: "POST",
      body: JSON.stringify({
        assistant: assistantId,
        initiating_memory: memoryId,
        collapse_type: collapseType,
        ritual_steps: {},
        restored_alignment: {},
        successful: true,
      }),
    }).then(() => alert("Recovery started"));
  };
  return (
    <div className="p-2 border rounded">
      <h5>Belief Recovery</h5>
      <input
        className="form-control mb-2"
        value={collapseType}
        onChange={(e) => setCollapseType(e.target.value)}
        placeholder="Collapse Type"
      />
      <button className="btn btn-primary" onClick={handleRun}>
        Run Ritual
      </button>
    </div>
  );
}
