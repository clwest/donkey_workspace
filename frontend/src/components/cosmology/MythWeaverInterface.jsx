import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythWeaverInterface({ assistantId }) {
  const [depth, setDepth] = useState(3);
  const [result, setResult] = useState(null);

  const runWeaver = () => {
    apiFetch("/myth-weaver/", { method: "POST", body: { assistant: assistantId, depth } })
      .then(setResult)
      .catch(() => setResult(null));
  };

  return (
    <div className="my-3">
      <h5>Myth Weaver</h5>
      <div className="input-group mb-2">
        <span className="input-group-text">Depth</span>
        <input
          type="number"
          value={depth}
          onChange={(e) => setDepth(parseInt(e.target.value, 10))}
          className="form-control"
        />
        <button className="btn btn-primary" onClick={runWeaver}>
          Weave
        </button>
      </div>
      {result && (
        <pre className="bg-light p-2 small">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}
