import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import { fetchRoleCollisions } from "../../api/ontology";

export default function AgentDashboardPage() {
  const [agents, setAgents] = useState([]);
  const [collisions, setCollisions] = useState([]);
  const [memoryCount, setMemoryCount] = useState(0);

  useEffect(() => {
    apiFetch(`/mcp/agent/`)
      .then(setAgents)
      .catch((err) => console.error("Error fetching agents:", err));
    fetchRoleCollisions()
      .then((res) => setCollisions(res || []))
      .catch(() => setCollisions([]));
    apiFetch(`/memory/list/`)
      .then((res) => setMemoryCount(res.length))
      .catch(() => setMemoryCount(0));
  }, []);

  return (
    <div className="container my-5">
      <h1 className="mb-4">🚀 Agent Mission Control</h1>

      <div className="row mb-4">
        <div className="col-md-4">
          <div className="border rounded p-3 h-100">
            <h5>Memory Status</h5>
            <p className="mb-0">Total Entries: {memoryCount}</p>
          </div>
        </div>
        <div className="col-md-8">
          <div className="border rounded p-3 h-100">
            <h5>Role Collisions</h5>
            {collisions.length === 0 ? (
              <p className="mb-0">None detected</p>
            ) : (
              <ul className="mb-0">
                {collisions.slice(0, 5).map((c, idx) => (
                  <li key={idx}>
                    {c.assistant_a} ↔ {c.assistant_b} ({c.tension_score})
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

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
}
