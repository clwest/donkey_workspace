import { useEffect, useState } from "react";
import { Modal, Button, OverlayTrigger, Tooltip } from "react-bootstrap";
import apiFetch from "../../utils/apiClient";

export default function AgentTrainingSuggestionModal({ show, onHide, agent }) {
  const [assistantSlug, setAssistantSlug] = useState(null);
  const [skills, setSkills] = useState([]);
  const [docs, setDocs] = useState([]);
  const [selectedDocs, setSelectedDocs] = useState([]);

  useEffect(() => {
    if (!show || !agent) return;
    async function load() {
      try {
        const primary = await apiFetch("/assistants/primary/");
        setAssistantSlug(primary.slug);
        const skillData = await apiFetch(`/assistants/${primary.slug}/skills/`);
        setSkills(skillData);
        const recDocs = await apiFetch(
          `/agents/${agent.id}/recommend-training-docs/`
        );
        setDocs(recDocs);
      } catch (err) {
        console.error("Failed to load training suggestions", err);
      }
    }
    load();
  }, [show, agent]);

  const toggleDoc = (id) => {
    setSelectedDocs((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    );
  };

  const handleAssign = async () => {
    if (!assistantSlug) return;
    try {
      await apiFetch(`/assistants/${assistantSlug}/assign-training/`, {
        method: "POST",
        body: { agent_id: agent.id, document_ids: selectedDocs },
      });
      setSelectedDocs([]);
      onHide();
    } catch (err) {
      console.error("Failed to assign training", err);
    }
  };

  const agentSkillNames = new Set(
    (agent.verified_skills || []).map((s) =>
      typeof s === "string" ? s : s.skill
    )
  );
  const missingSkills = skills.filter((s) => !agentSkillNames.has(s.name));

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Training Suggestions</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <h6>Current Verified Skills</h6>
        <ul>
          {(agent.verified_skills || []).map((s) => {
            const name = typeof s === "string" ? s : s.skill;
            return <li key={name}>{name}</li>;
          })}
          {(!agent.verified_skills || agent.verified_skills.length === 0) && (
            <li className="text-muted">No skills verified.</li>
          )}
        </ul>
        <h6>Missing Skills</h6>
        <ul>
          {missingSkills.map((s) => (
            <li key={s.id}>
              <OverlayTrigger
                placement="top"
                overlay={<Tooltip>{s.description}</Tooltip>}
              >
                <span>{s.name}</span>
              </OverlayTrigger>
            </li>
          ))}
          {missingSkills.length === 0 && (
            <li className="text-muted">No suggestions.</li>
          )}
        </ul>
        <h6>Recommended Documents</h6>
        <ul className="list-group">
          {docs.map((d) => (
            <li key={d.id} className="list-group-item">
              <label>
                <input
                  type="checkbox"
                  className="form-check-input me-2"
                  checked={selectedDocs.includes(d.id)}
                  onChange={() => toggleDoc(d.id)}
                />
                {d.title}
              </label>
            </li>
          ))}
          {docs.length === 0 && (
            <li className="list-group-item text-muted">No docs found.</li>
          )}
        </ul>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
        <Button
          variant="primary"
          onClick={handleAssign}
          disabled={selectedDocs.length === 0}
        >
          Assign Training
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
