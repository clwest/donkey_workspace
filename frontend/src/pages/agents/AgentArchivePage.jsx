import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import AgentReactivationVoteModal from "../../components/agents/AgentReactivationVoteModal";

export default function AgentArchivePage() {
  const [agents, setAgents] = useState([]);
  const [selected, setSelected] = useState(null);
  const [showVote, setShowVote] = useState(false);

  useEffect(() => {
    apiFetch("/agents/", { params: { is_active: "false" } })
      .then(setAgents)
      .catch((err) => console.error("Failed to load archived agents", err));
  }, []);

  const openVote = (agent) => {
    setSelected(agent);
    setShowVote(true);
  };

  const skillList = (agent) => {
    const skills = (agent.verified_skills || []).map((s) =>
      typeof s === "string" ? s : s.skill
    );
    return skills.slice(0, 3).join(", ") || "No skills";
  };

  return (
    <div className="container my-5">
      <h1 className="mb-4">Archived Agents</h1>
      <div className="row">
        {agents.map((a) => (
          <div key={a.id} className="col-md-4 mb-4">
            <div className="card p-3 h-100">
              <h5>{a.name}</h5>
              <p className="text-muted small mb-1">
                Last active {new Date(a.updated_at).toLocaleDateString()}
              </p>
              <p className="mb-1">Skills: {skillList(a)}</p>
              <p className="mb-2">{a.description}</p>
              <button
                className="btn btn-sm btn-outline-primary me-2"
                onClick={() => openVote(a)}
              >
                Propose Resurrection
              </button>
              <button
                className="btn btn-sm btn-primary"
                onClick={() =>
                  apiFetch(`/agents/${a.id}/reactivate/`, { method: "POST" })
                    .catch((err) => console.error("Reactivate failed", err))
                }
              >
                Reactivate Now
              </button>
            </div>
          </div>
        ))}
      </div>
      <AgentReactivationVoteModal
        show={showVote}
        onHide={() => setShowVote(false)}
        agent={selected}
      />
    </div>
  );
}
