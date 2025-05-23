import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function PersonaStageRenderer({ assistantId }) {
  const [persona, setPersona] = useState(null);

  useEffect(() => {
    if (!assistantId) return;
    apiFetch(`/simulation/roleplay-module/?assistant_id=${assistantId}`)
      .then((res) => setPersona(res))
      .catch(() => setPersona(null));
  }, [assistantId]);

  if (!persona) return <div className="text-muted">No persona.</div>;

  return (
    <div className="border p-2 mb-2">
      <strong>{persona.name}</strong> — {persona.archetype || "unknown"}
      <div className="small text-muted">{persona.purpose_signature}</div>
    </div>
  );
}
