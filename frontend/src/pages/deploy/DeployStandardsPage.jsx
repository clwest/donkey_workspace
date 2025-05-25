import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function DeployStandardsPage() {
  const [assistants, setAssistants] = useState([]);
  const [slug, setSlug] = useState("");
  const [goal, setGoal] = useState("");
  const [tags, setTags] = useState("");
  const [history, setHistory] = useState([]);
  const [result, setResult] = useState(null);

  useEffect(() => {
    apiFetch("/assistants/")
      .then((data) => setAssistants(data.results || []))
      .catch((err) => console.error("Failed to load assistants", err));
  }, []);

  const runEval = async () => {
    if (!slug || !goal.trim()) return;
    try {
      const res = await apiFetch("/deploy/standards/", {
        method: "POST",
        body: {
          assistant_slug: slug,
          goal,
          evaluation_tags: tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean),
        },
      });
      setResult(res);
      setHistory((h) => [res, ...h]);
    } catch (err) {
      console.error("Evaluation failed", err);
    }
  };

  return (
    <div className="container my-5">
      <h1 className="mb-3">Deployment Standards</h1>
      <div className="mb-3">
        <label className="form-label">Assistant</label>
        <select
          className="form-select"
          value={slug}
          onChange={(e) => setSlug(e.target.value)}
        >
          <option value="">Select assistant</option>
          {assistants.map((a) => (
            <option key={a.slug} value={a.slug}>
              {a.name}
            </option>
          ))}
        </select>
      </div>
      <div className="mb-3">
        <label className="form-label">Evaluation Goal</label>
        <textarea
          className="form-control"
          rows="3"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
        />
      </div>
      <div className="mb-3">
        <label className="form-label">Tags</label>
        <input
          type="text"
          className="form-control"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          placeholder="comma separated"
        />
      </div>
      <button className="btn btn-primary mb-3" onClick={runEval}>
        Run Evaluation
      </button>

      {result && (
        <div className="alert alert-secondary">
          <p className="mb-1">
            <strong>Result:</strong> {result.result}
          </p>
          <p className="mb-1 small text-muted">
            Tokens: {result.tokens_used} — Duration: {result.duration_ms} ms
            {result.reflection_id && (
              <>
                {" | "}
                <a href={`/reflections/${result.reflection_id}`}>View Reflection</a>
              </>
            )}
          </p>
        </div>
      )}

      {history.length > 3 && (
        <p className="mt-3 fw-semibold">Evaluation streak: {history.length}</p>
      )}

      {history.length > 0 && (
        <div className="mt-4">
          <h5>History</h5>
          {history.map((h, i) => (
            <div key={i} className="border rounded p-2 mb-2">
              <div>{h.result}</div>
              <div className="small text-muted">
                {h.tokens_used} tokens, {h.duration_ms} ms
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
