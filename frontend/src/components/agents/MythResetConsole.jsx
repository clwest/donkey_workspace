import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythResetConsole() {
  const [result, setResult] = useState(null);

  const runReset = async () => {
    try {
      const res = await apiFetch("/agents/myth-reset-cycle/", { method: "POST" });
      setResult(res);
    } catch (err) {
      console.error("reset failed", err);
    }
  };

  return (
    <div className="my-3">
      <button className="btn btn-outline-warning" onClick={runReset}>
        Run Myth Reset
      </button>
      {result && (
        <pre className="mt-2 small bg-light p-2 border">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
