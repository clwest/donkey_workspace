import { useState } from "react";
import { Modal, Button } from "react-bootstrap";
import { ONBOARDING_WORLD } from "../../onboarding/metadata";

export default function OnboardingHelpButton() {
  const [show, setShow] = useState(false);
  return (
    <>
      <button
        className="btn btn-outline-info position-fixed"
        style={{ bottom: "1rem", left: "1rem", zIndex: 1050 }}
        onClick={() => setShow(true)}
      >
        Need Help?
      </button>
      <Modal show={show} onHide={() => setShow(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Onboarding Steps</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ul className="list-unstyled">
            {ONBOARDING_WORLD.nodes.map((n) => (
              <li key={n.slug} className="mb-2">
                <strong>{n.title}</strong> — {n.tooltip || n.goal}
              </li>
            ))}
          </ul>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShow(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}
