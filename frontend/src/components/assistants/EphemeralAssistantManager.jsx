import { useState, useEffect } from "react";
import apiFetch from "../../utils/apiClient";
import { Modal, Button, Form } from "react-bootstrap";

export default function EphemeralAssistantManager() {
  const [assistants, setAssistants] = useState([]);
  const [show, setShow] = useState(false);
  const [name, setName] = useState("");
  const [expiration, setExpiration] = useState("");

  useEffect(() => {
    apiFetch("/assistants/", { params: { is_ephemeral: true } })
      .then(setAssistants)
      .catch(() => {});
  }, []);

  async function spawn() {
    await apiFetch("/assistants/", {
      method: "POST",
      body: { name, is_ephemeral: true, expiration_event: expiration || null },
    });
    const data = await apiFetch("/assistants/", { params: { is_ephemeral: true } });
    setAssistants(data);
    setShow(false);
    setName("");
    setExpiration("");
  }

  return (
    <div className="mt-4">
      <h5>Ephemeral Assistants</h5>
      <ul className="list-group mb-3">
        {assistants.map((a) => (
          <li key={a.id} className="list-group-item d-flex justify-content-between">
            <span>{a.name}</span>
            {a.expiration_event ? (
              <span className="text-muted">expires on event</span>
            ) : (
              <span className="text-muted">no expiration set</span>
            )}
          </li>
        ))}
      </ul>
      <Button onClick={() => setShow(true)}>Spawn Ephemeral Assistant</Button>

      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Spawn Ephemeral Assistant</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group className="mb-3">
            <Form.Label>Name</Form.Label>
            <Form.Control value={name} onChange={(e) => setName(e.target.value)} />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Expiration Event ID</Form.Label>
            <Form.Control
              value={expiration}
              onChange={(e) => setExpiration(e.target.value)}
              placeholder="Optional memory id"
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShow(false)}>
            Cancel
          </Button>
          <Button onClick={spawn} disabled={!name}>Create</Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}
