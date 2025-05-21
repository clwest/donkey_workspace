import { useState, useEffect } from "react";
import { Modal, Button } from "react-bootstrap";
import apiFetch from "../../utils/apiClient";

export default function RealignmentRequestModal({ show, onHide, agent }) {
  const [target, setTarget] = useState("");
  const [reason, setReason] = useState("");

  useEffect(() => {
    if (!show) {
      setTarget("");
      setReason("");
    }
  }, [show]);

  const submit = async () => {
    if (!agent || !target) return;
    try {
      await apiFetch(`/agents/${agent.id}/realign/`, {
        method: "POST",
        body: { target_cluster: target, reason },
      });
      onHide();
    } catch (err) {
      console.error("Realignment failed", err);
    }
  };

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>Realignment Request</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {agent && <p>Realign <strong>{agent.name}</strong>:</p>}
        <input
          className="form-control mb-2"
          value={target}
          onChange={(e) => setTarget(e.target.value)}
          placeholder="Target Cluster ID"
        />
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
        <Button variant="primary" onClick={submit} disabled={!target}>
          Submit
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
