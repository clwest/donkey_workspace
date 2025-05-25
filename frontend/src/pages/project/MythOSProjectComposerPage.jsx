import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythOSProjectComposerPage() {
  const [assistants, setAssistants] = useState([]);
  const [slug, setSlug] = useState("");
  const [goal, setGoal] = useState("");
  const [deadline, setDeadline] = useState("");
  const [tags, setTags] = useState("");
  const [result, setResult] = useState("");
  const [thoughts, setThoughts] = useState([]);

  useEffect(() => {
    apiFetch("/assistants/")
      .then((data) => setAssistants(data.results || []))
      .catch((err) => console.error("Failed to load assistants", err));
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
    if (tags) taskText += ` [${tags}]`;
    try {
      const res = await apiFetch(`/assistants/${slug}/run-task/`, {
        method: "POST",
        body: { task: taskText },
      });
      setResult(res.result || "");
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
