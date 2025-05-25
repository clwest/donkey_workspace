// frontend/components/agents/AssistantList.jsx
import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AgentList() {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    apiFetch(`/mcp/agents/`)
      .then(setAgents)
      .catch((err) => console.error("Failed to fetch agents:", err));
  }, []);

  return (
    <div className="container mt-5">
      <h2>🤖 Available agents</h2>
      <ul className="list-group">
        {agents.map((a) => (
          <li key={a.id} className="list-group-item">
            <strong>{a.name}</strong> – {a.description}
          </li>
        ))}
      </ul>
    </div>
  );
}