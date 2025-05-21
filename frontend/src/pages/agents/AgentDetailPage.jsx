import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import AgentFeedbackPanel from "../../components/agents/AgentFeedbackPanel";
import AgentTrainingPanel from "../../components/agents/AgentTrainingPanel";

const AgentDetailPage = () => {
  const { slug } = useParams();
  const [agent, setAgent] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    apiFetch(`/agents/${slug}/`)
      .then(setAgent)
      .catch((err) => console.error("Failed to load agent", err));
  }, [slug]);

  if (!agent) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-3">{agent.name}</h1>
      <ul className="nav nav-tabs mb-3">
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === "overview" ? "active" : ""}`}
            onClick={() => setActiveTab("overview")}
          >
            Overview
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === "feedback" ? "active" : ""}`}
            onClick={() => setActiveTab("feedback")}
          >
            Feedback
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === "training" ? "active" : ""}`}
            onClick={() => setActiveTab("training")}
          >
            Training
          </button>
        </li>
      </ul>

      {activeTab === "overview" && (
        <div>
          <p>
            <strong>Specialty:</strong> {agent.specialty || "N/A"}
          </p>
          <p>
            <strong>Description:</strong> {agent.description || "No description"}
          </p>
          <p>
            <strong>LLM:</strong> {agent.preferred_llm}
          </p>
          <p>
            <strong>Execution:</strong> {agent.execution_mode}
          </p>
        </div>
      )}
      {activeTab === "feedback" && <AgentFeedbackPanel agentId={agent.id} />}
      {activeTab === "training" && <AgentTrainingPanel agent={agent} />}
    </div>
  );
};

export default AgentDetailPage;
