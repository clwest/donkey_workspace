import { useState } from "react";
import apiFetch from "../utils/apiClient";

export default function ReflexiveEpistemologyDashboard({ assistantSlug }) {
  const [result, setResult] = useState(null);

  const runAudit = async () => {
    const data = await apiFetch(`/reflexive-epistemology/`, {
      method: "POST",
      body: { assistant: assistantSlug },
    });
    setResult(data);
  };

  return (
    <div className="p-3 border rounded bg-light">
      <h5>Reflexive Epistemology</h5>
      <button className="btn btn-sm btn-secondary mb-2" onClick={runAudit}>
        Run Audit
      </button>
      {result && (
        <pre className="small bg-white p-2 rounded">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
