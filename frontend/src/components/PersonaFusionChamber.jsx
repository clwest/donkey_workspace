import { useState } from "react";
import { createPersonaFusion } from "../api/agents";

export default function PersonaFusionChamber({ initiatorId, targetId, cardId }) {
  const [summary, setSummary] = useState("");
  const [archetype, setArchetype] = useState("");

  const runFusion = () => {
    createPersonaFusion({
      initiating_assistant: initiatorId,
      fused_with: targetId,
      resulting_identity_card: cardId,
      memory_alignment_summary: summary,
      fusion_archetype: archetype,
    }).then(() => {
      setSummary("");
      setArchetype("");
    });
  };

  return (
    <div className="p-2 border rounded">
      <h5>Persona Fusion</h5>
      <textarea
        className="form-control mb-2"
        placeholder="Memory alignment summary"
        value={summary}
        onChange={(e) => setSummary(e.target.value)}
      />
      <input
        className="form-control mb-2"
        placeholder="Fusion archetype"
        value={archetype}
        onChange={(e) => setArchetype(e.target.value)}
      />
      <button className="btn btn-primary" onClick={runFusion}>
        Fuse Personas
      </button>
    </div>
  );
}
