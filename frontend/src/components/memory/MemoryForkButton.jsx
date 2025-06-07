import { useState, useEffect } from "react";
import { Modal, Button, Form } from "react-bootstrap";
import apiFetch from "@/utils/apiClient";

export default function MemoryForkButton({ memoryId, assistantSlug, onForked }) {
  const [show, setShow] = useState(false);
  const [action, setAction] = useState("");
  const [notes, setNotes] = useState("");
  const [slug, setSlug] = useState(assistantSlug || null);
  const [outcome, setOutcome] = useState(null);

  useEffect(() => {
    async function fetchSlug() {
      if (!slug && show) {
        const data = await apiFetch(`/memory/${memoryId}/`);
        setSlug(data.linked_thought?.assistant_slug || null);
      }
    }
    fetchSlug();
  }, [show, slug, memoryId]);

  const handleSubmit = async () => {
    if (!slug) return;
    const data = await apiFetch(`/assistants/${slug}/simulate-memory/`, {
      method: "POST",
      body: {
        memory_id: memoryId,
        alternative_action: action,
        notes,
      },
    });
    if (data) {
      setOutcome(data.simulated_outcome);
      onForked && onForked();
    } else {
      alert("Failed to simulate memory");
    }
  };

  return (
    <>
      <button className="btn btn-outline-secondary" onClick={() => setShow(true)}>
        🔮 Simulate Alternate Outcome
      </button>
      <Modal show={show} onHide={() => setShow(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Simulate Alternate Outcome</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group className="mb-3">
            <Form.Label>Hypothetical Action</Form.Label>
            <Form.Control
              type="text"
              value={action}
              onChange={(e) => setAction(e.target.value)}
              placeholder="e.g. Ask for clarification"
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Notes / Prompt</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </Form.Group>
          {outcome && (
            <div className="alert alert-secondary">
              <strong>Simulated Outcome:</strong>
              <div className="mt-2" style={{ whiteSpace: "pre-wrap" }}>{outcome}</div>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShow(false)}>
            Close
          </Button>
          <Button variant="primary" onClick={handleSubmit} disabled={!slug}>
            Simulate
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}
