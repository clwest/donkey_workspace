import { useEffect, useState } from "react";
import { fetchCodexInteraction } from "../../api/agents";

export default function CodexInteractionLayer() {
  const [codex, setCodex] = useState(null);

  useEffect(() => {
    fetchCodexInteraction()
      .then(setCodex)
      .catch(() => setCodex(null));
  }, []);

  if (!codex) return null;

  return (
    <div className="p-2 border rounded">
      <h5>Codex Interaction</h5>
      <pre className="small mb-0">{JSON.stringify(codex, null, 2)}</pre>
    </div>
  );
}
