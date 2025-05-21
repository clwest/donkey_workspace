import { useState } from "react";
import apiFetch from "../utils/apiClient";

export default function MultiMythDecisionTool({ assistantSlug }) {
  const [scenario, setScenario] = useState("");
  const [weights, setWeights] = useState("{}");
  const [result, setResult] = useState(null);

  const runDecision = async () => {
    const data = await apiFetch(`/decision-frameworks/`, {
      method: "POST",
      body: {
        assistant: assistantSlug,
        linked_conscience: null,
        myth_weight_map: JSON.parse(weights || "{}"),
        scenario_description: scenario,
      },
    });
    setResult(data);
  };

  return (
    <div className="p-3 border rounded bg-light">
      <h5>Multi-Myth Decision Tool</h5>
      <textarea
        className="form-control mb-2"
        value={scenario}
        onChange={(e) => setScenario(e.target.value)}
        rows={3}
        placeholder="Describe scenario..."
      />
      <input
        className="form-control mb-2"
        value={weights}
        onChange={(e) => setWeights(e.target.value)}
        placeholder="{ mythId: weight }"
      />
      <button className="btn btn-sm btn-secondary" onClick={runDecision}>
        Evaluate
      </button>
      {result && (
        <pre className="small bg-white p-2 rounded mt-2">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
