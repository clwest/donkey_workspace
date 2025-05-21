import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

const AgentTrainingPanel = ({ agent }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [selectedDocs, setSelectedDocs] = useState([]);

  useEffect(() => {
    if (!agent) return;
    apiFetch(`/agents/${agent.id}/recommend-training-docs/`)
      .then(setRecommendations)
      .catch((err) => console.error("Failed to load recommendations", err));
  }, [agent]);

  const toggleDoc = (id) => {
    setSelectedDocs((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    );
  };

  const handleTrain = async () => {
    try {
      await apiFetch(`/agents/${agent.id}/train/`, {
        method: "POST",
        body: { document_ids: selectedDocs },
      });
      setSelectedDocs([]);
    } catch (err) {
      console.error("Training failed", err);
    }
  };

  return (
    <div>
      <h5>Skills</h5>
      <ul>
        {(agent.verified_skills || []).map((skill) => {
          const name = typeof skill === "string" ? skill : skill.skill;
          return <li key={name}>{name}</li>;
        })}
        {(!agent.verified_skills || agent.verified_skills.length === 0) && (
          <li className="text-muted">No skills yet.</li>
        )}
      </ul>
      <h5>Trained Documents</h5>
      <ul>
        {(agent.trained_documents || []).map((doc) => (
          <li key={doc.id}>{doc.title}</li>
        ))}
        {(!agent.trained_documents || agent.trained_documents.length === 0) && (
          <li className="text-muted">No documents trained.</li>
        )}
      </ul>
      <h5>Recommended Documents</h5>
      <ul className="list-group mb-2">
        {recommendations.map((doc) => (
          <li key={doc.id} className="list-group-item">
            <label>
              <input
                type="checkbox"
                className="form-check-input me-2"
                checked={selectedDocs.includes(doc.id)}
                onChange={() => toggleDoc(doc.id)}
              />
              {doc.title}
            </label>
          </li>
        ))}
        {recommendations.length === 0 && (
          <li className="list-group-item text-muted">No recommendations.</li>
        )}
      </ul>
      <button
        className="btn btn-sm btn-primary"
        onClick={handleTrain}
        disabled={selectedDocs.length === 0}
      >
        Train Agent
      </button>
    </div>
  );
};

export default AgentTrainingPanel;
