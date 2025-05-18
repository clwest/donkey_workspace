import { useEffect, useState } from "react";
import AgentCard from "../../components/agents/AgentCard";
import { Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

const AgentPage = () => {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    apiFetch("/agents/")
      .then((data) => setAgents(data))
      .catch((err) => console.error("Failed to fetch agents:", err));
  }, []);

return (
    <div className="container my-5">
      <h1 className="mb-4">🚀 Agent Mission Control</h1>

      {/* Core tools grid */}
      {agents.map((a) => (
        <div key={a.id} className="col-md-4 mb-4">
            <AgentCard agent={a} />
        </div>
        ))}

      <hr className="my-5" />

      <h3 className="mb-3">🤖 Your agents</h3>
      <div className="row">
        {agents.map((a) => (
          <div key={a.id} className="col-md-4 mb-4">
            <div className="card p-3 shadow-sm h-100">
              <h5>
                <Link to={`/agents/${a.slug}`} className="text-decoration-none">
                  🧠 {a.name}
                </Link>
              </h5>
              <p className="text-muted small mb-2">{a.specialty || "Generalist"}</p>
              <p className="mb-1">{a.description}</p>
              <Link to={`/agents/${a.slug}`} className="btn btn-sm btn-outline-primary mt-auto">
                View Agent
              </Link>
            </div>
          </div>
        ))}
      </div>

      <Link to="/projects" className="btn btn-outline-secondary mt-4">
        🔙 Back to Projects
      </Link>
    </div>
  );
};

export default AgentPage;