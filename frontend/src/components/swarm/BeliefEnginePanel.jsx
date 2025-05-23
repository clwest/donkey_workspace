import { useEffect, useState } from "react";
import { updateBeliefEngine } from "../../api/agents";

export default function BeliefEnginePanel({ assistantId }) {
  const [updating, setUpdating] = useState(false);
  const [result, setResult] = useState(null);

  const runUpdate = async () => {
    setUpdating(true);
    try {
      const res = await updateBeliefEngine(assistantId);
      setResult(res.updated_alignment);
    } catch (err) {
      console.error("Failed to update belief engine", err);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="my-3">
      <button className="btn btn-sm btn-primary" onClick={runUpdate} disabled={updating}>
        Update Belief Engine
      </button>
      {result && (
        <pre className="mt-2 small bg-light p-2">{JSON.stringify(result)}</pre>
      )}
    </div>
  );
}
