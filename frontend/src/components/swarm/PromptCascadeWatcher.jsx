import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function PromptCascadeWatcher({ promptId }) {
  const [cascade, setCascade] = useState(null);

  useEffect(() => {
    if (!promptId) return;
    apiFetch(`/simulation/prompt-cascades/${promptId}/`)
      .then((res) => setCascade(res))
      .catch(() => setCascade(null));
  }, [promptId]);

  if (!promptId) return null;

  return (
    <div className="my-3">
      <h5>Prompt Cascade</h5>
      {!cascade && <div>Loading...</div>}
      {cascade && (
        <pre className="small bg-light p-2 rounded">
          {JSON.stringify(cascade, null, 2)}
        </pre>
      )}
    </div>
  );
}
