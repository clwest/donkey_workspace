import { useState } from "react";
import apiFetch from "../utils/apiClient";

export default function InsightPlanner({ assistantId }) {
  const [context, setContext] = useState("");
  const [plan, setPlan] = useState(null);

  const generate = async () => {
    const data = await apiFetch(`/assistants/${assistantId}/generate-plan/`, {
      method: "POST",
      body: JSON.stringify({ context }),
    });
    setPlan(data.plan || []);
  };

  return (
    <div className="mb-3">
      <input
        className="form-control mb-2"
        placeholder="Context filter"
        value={context}
        onChange={(e) => setContext(e.target.value)}
      />
      <button className="btn btn-secondary" onClick={generate}>
        Generate Plan
      </button>
      {plan && (
        <ol className="mt-2">
          {plan.map((step, idx) => (
            <li key={idx}>{step}</li>
          ))}
        </ol>
      )}
    </div>
  );
}
