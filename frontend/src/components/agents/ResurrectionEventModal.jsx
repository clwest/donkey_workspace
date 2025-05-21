import { useState, useEffect } from "react";
import { Modal, Button } from "react-bootstrap";

export default function ResurrectionEventModal({ show, onHide, legacy, onConfirm }) {
  const [reason, setReason] = useState("");

  useEffect(() => {
    if (!show) setReason("");
  }, [show]);

  const confirm = () => {
    if (!legacy) return;
    onConfirm && onConfirm(reason);
    setReason("");
    onHide();
  };

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>Resurrect Legacy Agent</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {legacy && (
          <p>
            Revive <strong>{legacy.agent_name || legacy.agent?.name}</strong>
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
        <Button variant="primary" onClick={confirm} disabled={!reason}>
          Confirm
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
