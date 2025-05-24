// pages/assistants/reflections/AssistantReflectPage.jsx

import { useParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";
import ThoughtLogCard from "../../../components/assistant/thoughts/ThoughtLogCard";
import ReflectionToastStatus from "../../../components/assistant/ReflectionToastStatus";

export default function AssistantReflectPage() {
  const { slug } = useParams();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [toastStatus, setToastStatus] = useState(null);

  const reflect = async (force = false) => {
    setLoading(true);
    try {
      const res = await apiFetch(`/assistants/${slug}/reflect-now/`, {
        method: "POST",
        params: force ? { force: "true" } : undefined,
      });
      if (res.status === "ok") {
        await loadReflectionLogs();
        setToastStatus("success");
      } else {
        setToastStatus("error");
      }
    } catch (err) {
      console.error("Reflection failed", err);
      const detail = err?.statusText || err?.message;
      const msg = detail
        ? `Reflection request failed: ${detail}`
        : "Reflection request failed";
      console.error(msg);
      setToastStatus("error");
    } finally {
      setLoading(false);
    }
  };

  const loadReflectionLogs = async () => {
    try {
      const res = await apiFetch(`/assistants/${slug}/reflections/recent/`);
      setLogs(res.thoughts || []);
    } catch (err) {
      console.error("Failed to load reflection logs", err);
    }
  };

  const updateFeedback = async (id, value) => {
    try {
      await apiFetch(`/assistants/thoughts/${id}/feedback/`, {
        method: "PATCH",
        body: { feedback: value },
      });

      setLogs((prev) =>
        prev.map((log) =>
          log.id === id ? { ...log, feedback: value } : log
        )
      );
    } catch (err) {
      console.error("Feedback update failed", err);
    }
  };

  useEffect(() => {
    reflect();
  }, [slug]);

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">🪞 Assistant Reflection: {slug}</h2>
        <div className="btn-group" role="group">
          <button
            className="btn btn-primary"
            onClick={() => reflect(false)}
            disabled={loading}
          >
            {loading ? "Reflecting..." : "🔁 Run Reflection"}
          </button>
          <button
            className="btn btn-outline-warning"
            onClick={() => reflect(true)}
            disabled={loading}
          >
            Force Refresh
          </button>
        </div>
        <Link to={`/assistants/${slug}`} className="btn btn-outline-secondary">
          🔙 Back to Assistant
        </Link>
      </div>

      {logs.length > 0 && (
        <div className="card mb-5 shadow-sm border-info">
          <div className="card-header bg-info text-white">
            <strong>Latest Reflection Summary</strong>
          </div>
          <div className="card-body">
            <pre className="mb-0 text-wrap">{logs[0].content}</pre>
          </div>
        </div>
      )}

      <h4 className="mb-3">🧠 Recent Thought Logs</h4>

      {logs.length === 0 ? (
        <p className="text-muted">No recent reflections saved yet.</p>
      ) : (
        logs.map((log) => (
          <div key={log.id}>
            <ThoughtLogCard thought={log} />
            <div className="d-flex align-items-center gap-3 mb-4">
              <select
                className="form-select form-select-sm w-auto ms-auto"
                value={log.feedback || ""}
                onChange={(e) => updateFeedback(log.id, e.target.value)}
              >
                <option value="">💬 Feedback</option>
                <option value="perfect">✅ Perfect</option>
                <option value="helpful">👍 Helpful</option>
                <option value="not_helpful">👎 Not Helpful</option>
                <option value="too_long">💤 Too Long</option>
                <option value="too_short">⚡ Too Short</option>
                <option value="irrelevant">❌ Irrelevant</option>
                <option value="unclear">❓ Unclear</option>
              </select>
            </div>
          </div>
        ))
      )}
    </div>
    <ReflectionToastStatus status={toastStatus} />
  );
}