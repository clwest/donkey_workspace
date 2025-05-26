import { useState } from "react";
import { startStabilizationCampaign } from "../../api/ontology";

export default function StabilizationCampaignPage() {
  const [clauseId, setClauseId] = useState("");
  const [result, setResult] = useState(null);

  const launch = () => {
    if (!clauseId) return;
    startStabilizationCampaign(clauseId)
      .then(setResult)
      .catch((e) => console.error(e));
  };

  return (
    <div className="container my-4">
      <h1 className="mb-3">Clause Stabilization Campaign</h1>
      <div className="input-group mb-3" style={{ maxWidth: "400px" }}>
        <input
          className="form-control"
          placeholder="Clause ID"
          value={clauseId}
          onChange={(e) => setClauseId(e.target.value)}
        />
        <button className="btn btn-primary" onClick={launch}>
          Launch
        </button>
      </div>
      {result && (
        <pre className="bg-light p-2 rounded">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
