import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

export default function CodexPromptOrchestrator() {
  const { assistantId } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    apiFetch(`/codex/orchestrator/`, { params: { assistant_id: assistantId } })
      .then(setData)
      .catch((err) => console.error("Failed to load orchestrator", err));
  }, [assistantId]);

  return (
    <div className="container my-4">
      <h3>Prompt Orchestrator</h3>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
