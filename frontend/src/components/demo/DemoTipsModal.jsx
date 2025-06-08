import { useEffect, useState } from "react";
import { Modal, Button } from "react-bootstrap";
import DemoTipsSidebar from "./DemoTipsSidebar";

export default function DemoTipsModal({ show, onClose, slug, sessionId }) {
  const [open, setOpen] = useState(false);
  useEffect(() => setOpen(show), [show]);
  return (
    <Modal show={open} onHide={onClose} size="lg" centered>
      <Modal.Header closeButton>
        <Modal.Title>What can I ask?</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <DemoTipsSidebar slug={slug} sessionId={sessionId} />
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
