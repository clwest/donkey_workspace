import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

const AgentFeedbackPanel = ({ agentId }) => {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    if (!agentId) return;
    apiFetch(`/agents/${agentId}/feedback/`)
      .then(setLogs)
      .catch((err) => console.error("Failed to load feedback", err));
  }, [agentId]);

  const handleUpdate = async () => {
    try {
      await apiFetch(`/agents/${agentId}/update-from-feedback/`, {
        method: "POST",
        body: { feedback: [] },
      });
      const data = await apiFetch(`/agents/${agentId}/feedback/`);
      setLogs(data);
    } catch (err) {
      console.error("Update failed", err);
    }
  };

  return (
    <div>
      <button className="btn btn-sm btn-primary mb-2" onClick={handleUpdate}>
        Update from Feedback
      </button>
      <ul className="list-group">
        {logs.map((log) => (
          <li key={log.id} className="list-group-item">
            <div className="d-flex justify-content-between">
              <span>{log.feedback_text}</span>
              {log.score !== null && (
                <span className="badge bg-secondary">{log.score}</span>
              )}
            </div>
            <small className="text-muted">{log.feedback_type}</small>
          </li>
        ))}
        {logs.length === 0 && (
          <li className="list-group-item text-muted">No feedback yet.</li>
        )}
      </ul>
    </div>
  );
};

export default AgentFeedbackPanel;
