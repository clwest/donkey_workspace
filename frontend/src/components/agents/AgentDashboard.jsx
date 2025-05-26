import { useEffect, useState } from "react";
import AgentCard from "./AgentCard";
import { fetchAgents } from "../../api/agents";
import { Link } from "react-router-dom";

export default function AgentDashboard() {
  const [agents, setAgents] = useState([]);
  // filter state for execution style and LLM
  const [styleFilter, setStyleFilter] = useState("all");
  const [llmFilter, setLlmFilter] = useState("all");

  useEffect(() => {
    fetchAgents()
      .then(setAgents)
      .catch((err) => console.error("Failed to load agents", err));
  }, []);

  const filtered = agents.filter((a) => {
    const style = a.execution_style || a.execution_mode;
    return (
      (styleFilter === "all" || style === styleFilter) &&
      (llmFilter === "all" || a.preferred_llm === llmFilter)
    );
  });

  return (
    <div>
      <div className="row mb-3">
        <div className="col-md-3">
          <select
            className="form-select"
            value={styleFilter}
            onChange={(e) => setStyleFilter(e.target.value)}
          >
            <option value="all">All Execution Styles</option>
            {[...new Set(agents.map((a) => a.execution_style || a.execution_mode))].map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
        <div className="col-md-3">
          <select
            className="form-select"
            value={llmFilter}
            onChange={(e) => setLlmFilter(e.target.value)}
          >
            <option value="all">All LLMs</option>
            {[...new Set(agents.map((a) => a.preferred_llm))].map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="row">
        {filtered.map((a) => (
          <div key={a.id} className="col-md-4 mb-4">
            <AgentCard agent={a} />
          </div>
        ))}
      </div>
      <Link to="/projects" className="btn btn-outline-secondary mt-4">
        🔙 Back to Projects
      </Link>
    </div>
  );
}
