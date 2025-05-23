import { useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function AnamnesisEngineConsole() {
  const [slug, setSlug] = useState("");
  const [result, setResult] = useState(null);

  const runRetrieval = async () => {
    if (!slug) return;
    const res = await apiFetch("/memory/anamnesis/", {
      method: "POST",
      body: { assistant_slug: slug },
    });
    setResult(res);
  };

  return (
    <div className="my-3">
      <h5>Anamnesis Engine</h5>
      <div className="input-group mb-2">
        <input
          type="text"
          className="form-control"
          placeholder="Assistant slug"
          value={slug}
          onChange={(e) => setSlug(e.target.value)}
        />
        <button className="btn btn-secondary" onClick={runRetrieval}>
          Recall
        </button>
      </div>
      {result && (
        <pre className="small bg-light p-2 border">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
