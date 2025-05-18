import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function AgentDemosPage() {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    fetch("/api/agent/demos/")
      .then((res) => res.json())
      .then((data) => setAgents(data))
      .catch((err) => console.error("Failed to fetch demo agents:", err));
  }, []);

  return (
    <div className="container py-5">
      <h1 className="mb-4">🧪 AI Agent Demos</h1>
      <div className="row">
        {agents.map((agent) => (
          <div key={agent.id} className="col-md-4 mb-4">
            <div className="card h-100 shadow-sm border-0">
              <div className="card-body">
                <div className="d-flex align-items-center mb-3">
                  {agent.avatar ? (
                    <img
                      src={agent.avatar}
                      alt={agent.name}
                      className="rounded-circle me-3"
                      style={{ width: "50px", height: "50px", objectFit: "cover" }}
                    />
                  ) : (
                    <div
                      className="rounded-circle bg-secondary me-3 d-flex justify-content-center align-items-center"
                      style={{ width: "50px", height: "50px", color: "white" }}
                    >
                      🤖
                    </div>
                  )}
                  <h5 className="mb-0">{agent.name}</h5>
                </div>
                <p className="text-muted" style={{ fontSize: "0.9rem" }}>
                  {agent.description || "No description provided."}
                </p>
                {agent.specialty && (
                  <span className="badge bg-info text-dark">{agent.specialty}</span>
                )}
              </div>
              <div className="card-footer bg-transparent border-0 text-end">
                <Link
                  to={`/assistants/${agent.slug}`}
                  className="btn btn-outline-primary btn-sm"
                >
                  View Details
                </Link>
                <div>
                <Link to={`/chat/${agent.slug}`} className="btn btn-outline-primary btn-sm mt-2">
                    💬 Chat
                </Link>
                </div>
              </div>
            </div>
          </div>
        ))}
        {agents.length === 0 && (
          <p className="text-muted text-center">No demo agents available yet.</p>
        )}
      </div>
    </div>
  );
}
