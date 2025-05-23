import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AssistantAlignmentToolset({ assistantId }) {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    if (!assistantId) return;
    apiFetch(`/assistants/${assistantId}/economy/`)
      .then((res) => setMetrics(res))
      .catch(() => setMetrics(null));
  }, [assistantId]);

  if (!metrics) return <div>Loading alignment...</div>;

  return (
    <div className="my-3">
      <h5>Economic Alignment</h5>
      <p>Codex Score Alignment: {metrics.codex_score}</p>
      <p>Directive Fulfillment Curve: {metrics.directive_curve}</p>
      <p>Symbolic Productivity Index: {metrics.productivity_index}</p>
      <div className="mt-2">
        <strong>Resonance Level:</strong> {metrics.economic_resonance}
      </div>
      {metrics.optimization_tips && metrics.optimization_tips.length > 0 && (
        <div className="mt-2">
          <h6>Optimization Tips</h6>
          <ul className="list-unstyled">
            {metrics.optimization_tips.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
