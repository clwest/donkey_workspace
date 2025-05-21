import { useState } from "react";
import { Modal, Button } from "react-bootstrap";
import apiFetch from "../../utils/apiClient";

export default function DreamTrainer({ assistant }) {
  const [scenario, setScenario] = useState(null);
  const [accepted, setAccepted] = useState(false);
  const [reflection, setReflection] = useState("");

  const openScenario = async () => {
    try {
      const data = await apiFetch(`/assistants/${assistant.slug}/dream-scenario/`);
      setScenario(data);
    } catch (err) {
      console.error("Failed to load scenario", err);
    }
  };

  const submitReflection = async () => {
    try {
      await apiFetch(`/assistants/${assistant.slug}/dream-scenario/`, {
        method: "POST",
        body: { reflection },
      });
      setScenario(null);
      setAccepted(false);
      setReflection("");
    } catch (err) {
      console.error("Failed to submit reflection", err);
    }
  };

  return (
    <div className="my-3">
      <button className="btn btn-outline-primary" onClick={openScenario}>
        Dream Training
      </button>
      {scenario && (
        <Modal show onHide={() => setScenario(null)}>
          <Modal.Header closeButton>
            <Modal.Title>Dream Scenario</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <pre className="mb-3">{scenario.challenge}</pre>
            {accepted ? (
              <div>
                <textarea
                  className="form-control mb-2"
                  rows="4"
                  value={reflection}
                  onChange={(e) => setReflection(e.target.value)}
                  placeholder="Your reflection"
                />
                <Button variant="success" onClick={submitReflection}>
                  Submit Reflection
                </Button>
              </div>
            ) : (
              <div>
                <Button
                  variant="secondary"
                  onClick={() => setScenario(null)}
                  className="me-2"
                >
                  Decline
                </Button>
                <Button variant="primary" onClick={() => setAccepted(true)}>
                  Accept Challenge
                </Button>
              </div>
            )}
          </Modal.Body>
        </Modal>
      )}
    </div>
  );
}
