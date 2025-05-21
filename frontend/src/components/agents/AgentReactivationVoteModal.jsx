import { useState, useEffect } from "react";
import { Modal, Button } from "react-bootstrap";
import apiFetch from "../../utils/apiClient";

export default function AgentReactivationVoteModal({ show, onHide, agent }) {
  const [reason, setReason] = useState("");

  useEffect(() => {
    if (!show) setReason("");
  }, [show]);

  const submitVote = async () => {
    if (!agent) return;
    try {
      await apiFetch(`/agents/${agent.id}/reactivation-votes/`, {
        method: "POST",
        body: { reason },
      });
      setReason("");
      onHide();
    } catch (err) {
      console.error("Failed to submit vote", err);
    }
  };

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>Propose Resurrection</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {agent && (
          <p>
            Voting to reactivate <strong>{agent.name}</strong>
          </p>
        )}
        <textarea
          className="form-control"
          rows="3"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Reason"
        />
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button variant="primary" onClick={submitVote} disabled={!reason}>
          Submit Vote
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
