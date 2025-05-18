// frontend/components/mcp_core/ReflectionSuccessModal.jsx

import { Modal, Button } from "react-bootstrap";

export default function ReflectionSuccessModal({ show, onHide, reflectionId }) {
  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>🎯 Reflection Created!</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p>Your custom reflection has been successfully generated and saved. 🧠✨</p>
        <p>What would you like to do next?</p>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="primary" href={`/reflections/${reflectionId}`}>
          View Reflection
        </Button>
        <Button variant="success" href="/reflections/custom">
          Start Another
        </Button>
        <Button variant="secondary" href="/reflections">
          Reflection Dashboard
        </Button>
      </Modal.Footer>
    </Modal>
  );
}