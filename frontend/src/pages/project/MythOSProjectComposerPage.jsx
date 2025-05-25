import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythOSProjectComposerPage() {
  const [assistants, setAssistants] = useState([]);
  const [slug, setSlug] = useState("");
  const [goal, setGoal] = useState("");
  const [deadline, setDeadline] = useState("");
  const [difficulty, setDifficulty] = useState("easy");
  const [needsReflection, setNeedsReflection] = useState(false);
  const [tags, setTags] = useState("");
  const [result, setResult] = useState("");
  const [thoughts, setThoughts] = useState([]);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    apiFetch("/assistants/")
      .then((data) => setAssistants(data.results || []))
      .catch((err) => console.error("Failed to load assistants", err));
  }, []);

  useEffect(() => {
    const d = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
      .toISOString()
      .slice(0, 10);
    setDeadline(d);
  }, []);

  useEffect(() => {
    if (slug) {
      apiFetch(`/assistants/${slug}/thoughts/recent/`)
        .then((data) => setThoughts(data.thoughts || []))
        .catch((err) => console.error("Failed to load thoughts", err));
    }
  }, [slug]);

  const runTask = async () => {
    if (!slug || !goal.trim()) return;
    let taskText = goal;
    if (deadline) taskText += ` (deadline: ${deadline})`;
    if (difficulty) taskText += ` [difficulty: ${difficulty}]`;
    if (tags) taskText += ` [${tags}]`;
    try {
      const res = await apiFetch(`/assistants/${slug}/run-task/`, {
        method: "POST",
        body: { task: taskText },
      });
      setResult(res.result || "");
      setHistory((h) => [
        {
          id: res.log_id,
          result: res.result,
          tokens: res.token_usage,
          duration: res.duration_ms,
          difficulty,
          reflection: null,
        },
        ...h,
      ]);
      if (needsReflection) {
        try {
          const refRes = await apiFetch(`/assistants/${slug}/reflect-now/`, {
            method: "POST",
          });
          setHistory((h) => [{ ...h[0], reflection: refRes.log_id }, ...h.slice(1)]);
        } catch (err) {
          console.error("Reflection failed", err);
        }
      }
      const thoughtRes = await apiFetch(`/assistants/${slug}/thoughts/recent/`);
      setThoughts(thoughtRes.thoughts || []);
    } catch (err) {
      console.error("Run task failed", err);
      setResult("Failed to run task");
    }
  };

  return (
    <div className="container my-4">
      <h3 className="mb-3">Project Composer</h3>
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
        <label className="form-label">Goal / Task</label>
        <textarea
          className="form-control"
          rows="3"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
        />
      </div>
      <div className="mb-3">
        <label className="form-label">Deadline</label>
        <input
          type="date"
          className="form-control"
          value={deadline}
          onChange={(e) => setDeadline(e.target.value)}
        />
      </div>
      <div className="mb-3">
        <label className="form-label">Difficulty</label>
        <select
          className="form-select"
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
        >
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
      </div>
      <div className="form-check mb-3">
        <input
          className="form-check-input"
          type="checkbox"
          id="needsRef"
          checked={needsReflection}
          onChange={(e) => setNeedsReflection(e.target.checked)}
        />
        <label className="form-check-label" htmlFor="needsRef">
          Requires Reflection?
        </label>
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
      <button className="btn btn-primary mb-3" onClick={runTask}>
        Run Task
      </button>
      {result && (
        <div className="alert alert-secondary">
          <pre className="mb-0">{result}</pre>
        </div>
      )}
      {history.length > 0 && (
        <div className="mt-4">
          <h5>Planning History</h5>
          {history.map((h, idx) => (
            <details key={idx} className="mb-2">
              <summary className="fw-semibold">Run {idx + 1}</summary>
              <div className="p-2 border rounded">
                <p className="mb-1">
                  <strong>Result:</strong> {h.result}
                </p>
                <p className="mb-1 small text-muted">
                  Tokens: {h.tokens.total} (p{h.tokens.prompt}/c{h.tokens.completion})
                  , Duration: {h.duration} ms
                  , Difficulty: {h.difficulty}
                </p>
                {h.reflection && (
                  <p className="mb-0 small">Reflection Log: {h.reflection}</p>
                )}
              </div>
            </details>
          ))}
        </div>
      )}
      {thoughts.length > 0 && (
        <div className="mt-4">
          <h5>Recent Planning Thoughts</h5>
          <ul className="list-group">
            {thoughts.map((t) => (
              <li key={t.id || t.thought} className="list-group-item">
                {t.thought}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
