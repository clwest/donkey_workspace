import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { fetchTrainedAgents, promoteTrainedAgent } from "../../api/agents";
import TrainedAgentCard from "../../components/agents/TrainedAgentCard";

export default function TrainedAgentsPage() {
  const [logs, setLogs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchTrainedAgents()
      .then(setLogs)
      .catch((err) => console.error("Failed to load trained agents", err));
  }, []);

  const handlePromote = async (id) => {
    try {
      const assistant = await promoteTrainedAgent(id);
      setLogs((prev) => prev.filter((l) => l.id !== id));
      toast.success("✅ Assistant successfully promoted.");
      if (assistant && assistant.id) {
        navigate(`/assistants/${assistant.id}/interface`);
      }
    } catch (err) {
      console.error("Promotion failed", err);
      toast.error("❌ Promotion failed. Check backend logs.");
    }
  };

  return (
    <div className="container my-5">
      <h2 className="mb-4">Symbolic Training Sessions</h2>
      <div className="row">
        {logs.map((log) => (
          <div key={log.id} className="col-md-4 mb-4">
            <TrainedAgentCard log={log} onPromote={() => handlePromote(log.id)} />
          </div>
        ))}
        {logs.length === 0 && (
          <p className="text-muted">No trained agents found.</p>
        )}
      </div>
    </div>
  );
}
