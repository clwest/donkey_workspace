// frontend/components/agents/AssistantList.jsx
import { useEffect, useState } from "react";

export default function AgentList() {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/mcp/agents/")
      .then((res) => res.json())
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