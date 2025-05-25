import { useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function AssistantRunTaskPanel({ slug }) {
  const [task, setTask] = useState("");
  const [result, setResult] = useState("");
  const [running, setRunning] = useState(false);

  const runTask = async () => {
    if (!task.trim()) return;
    setRunning(true);
    try {
      const res = await apiFetch(`/assistants/${slug}/run-task/`, {
        method: "POST",
        body: { task },
      });
      setResult(res.result || "");
    } catch (err) {
      console.error("Run task failed", err);
      setResult("Failed to run task");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="p-2 border rounded">
      <h5>Run Task</h5>
      <textarea
        className="form-control mb-2"
        rows="3"
        value={task}
        onChange={(e) => setTask(e.target.value)}
        placeholder="Enter a task..."
      />
      <button className="btn btn-sm btn-primary" onClick={runTask} disabled={running}>
        {running ? "Running..." : "Run"}
      </button>
      {result && (
        <div className="mt-3">
          <strong>Result:</strong>
          <pre className="mt-1">{result}</pre>
        </div>
      )}
    </div>
  );
}
