import { Modal, Button } from "react-bootstrap";

export default function TeachAnchorModal({ show, onClose }) {
  return (
    <Modal show={show} onHide={onClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Glossary Updated</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        You’ve just taught your assistant their first concept!
      </Modal.Body>
      <Modal.Footer>
        <Button variant="primary" onClick={onClose}>
          Continue
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
