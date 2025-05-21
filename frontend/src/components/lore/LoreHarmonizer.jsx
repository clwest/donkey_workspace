import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function LoreHarmonizer() {
  const [report, setReport] = useState(null);
  async function run() {
    try {
      const data = await apiFetch("/agents/harmonize-global/");
      setReport(data);
    } catch (err) {
      console.error("Harmonization failed", err);
    }
  }

  return (
    <div className="my-3">
      <button className="btn btn-primary" onClick={run}>
        Harmonize Narrative
      </button>
      {report && (
        <pre className="bg-light p-3 mt-3 border rounded">
          {JSON.stringify(report, null, 2)}
        </pre>
      )}
    </div>
  );
}
