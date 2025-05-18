// frontend/components/GlobalSuccessModal.jsx

import { Modal, Button } from "react-bootstrap";
import { Link } from "react-router-dom";

export default function GlobalSuccessModal({ show, onClose, title, message, linkTo, linkLabel = "View" }) {
  return (
    <Modal show={show} onHide={onClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>{title || "Success!"}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p>{message || "Your action was completed successfully."}</p>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>
          Close
        </Button>
        {linkTo && (
          <Link to={linkTo}>
            <Button variant="primary">
              {linkLabel}
            </Button>
          </Link>
        )}
      </Modal.Footer>
    </Modal>
  );
}