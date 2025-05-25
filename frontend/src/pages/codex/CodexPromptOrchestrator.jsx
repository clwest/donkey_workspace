import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

export default function CodexPromptOrchestrator() {
  const { assistantId } = useParams();
  const [data, setData] = useState(null);
  const [assistant, setAssistant] = useState(null);

  useEffect(() => {
    apiFetch(`/codex/orchestrator/`, { params: { assistant_id: assistantId } })
      .then(setData)
      .catch((err) => console.error("Failed to load orchestrator", err));
    apiFetch(`/assistants/${assistantId}/`)
      .then(setAssistant)
      .catch((err) => console.error("Failed to load assistant", err));
  }, [assistantId]);

  return (
    <div className="container my-4">
      <h3>Prompt Orchestrator</h3>
      {assistant && (
        <h5 className="text-muted">Assistant: {assistant.name}</h5>
      )}
      {data ? (
        <pre>{JSON.stringify(data, null, 2)}</pre>
      ) : (
        <div className="text-muted">No orchestrator data.</div>
      )}
    </div>
  );
}
