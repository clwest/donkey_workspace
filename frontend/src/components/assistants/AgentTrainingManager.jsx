import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import {
  assignTrainingDocuments,
  evaluateAgentTraining,
} from "../../api/assistants";

export default function AgentTrainingManager({ assistantSlug }) {
  const [agents, setAgents] = useState([]);
  const [docs, setDocs] = useState([]);
  const [agentId, setAgentId] = useState("");
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch(`/agents/`);
        setAgents(res);
        const docsRes = await apiFetch(`/intel/documents/?limit=50`);
        setDocs(docsRes);
      } catch (err) {
        console.error("Failed to load training data", err);
      }
    }
    load();
  }, [assistantSlug]);

  const toggleDoc = (id) => {
    setSelectedDocs((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    );
  };

  const handleAssign = async () => {
    if (!agentId || selectedDocs.length === 0) return;
    setLoading(true);
    try {
      await assignTrainingDocuments(assistantSlug, agentId, selectedDocs);
      const rep = await evaluateAgentTraining(assistantSlug, agentId);
      setReport(rep);
      setSelectedDocs([]);
    } catch (err) {
      console.error("Training assignment failed", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-2">
        <label className="form-label me-2">Agent:</label>
        <select
          className="form-select d-inline w-auto"
          value={agentId}
          onChange={(e) => setAgentId(e.target.value)}
        >
          <option value="">Select agent</option>
          {agents.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name}
            </option>
          ))}
        </select>
      </div>
      <div className="mb-2">
        <h6>Documents</h6>
        <ul className="list-group">
          {docs.map((d) => (
            <li key={d.id} className="list-group-item">
              <label>
                <input
                  type="checkbox"
                  className="form-check-input me-2"
                  checked={selectedDocs.includes(d.id)}
                  onChange={() => toggleDoc(d.id)}
                />
                {d.title}
              </label>
            </li>
          ))}
        </ul>
      </div>
      <button
        className="btn btn-primary mb-3"
        onClick={handleAssign}
        disabled={!agentId || selectedDocs.length === 0 || loading}
      >
        {loading ? "Assigning..." : "Assign Training"}
      </button>
      {report && (
        <div className="alert alert-info">
          <p className="mb-1">
            Completed: {report.completed_assignments} | Pending: {report.pending_assignments}
          </p>
          {report.avg_feedback !== null && (
            <p className="mb-1">Avg Feedback: {report.avg_feedback.toFixed(2)}</p>
          )}
          <p className="mb-1">Next: {report.next_steps}</p>
        </div>
      )}
    </div>
  );
}
