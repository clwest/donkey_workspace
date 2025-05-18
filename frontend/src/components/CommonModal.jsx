import React from "react";
import { Modal, Button } from "react-bootstrap";

export default function CommonModal({
  show,
  onClose,
  title,
  children,
  footer,
}) {
  return (
    <Modal show={show} onHide={onClose} centered>
      {title && (
        <Modal.Header closeButton>
          <Modal.Title>{title}</Modal.Title>
        </Modal.Header>
      )}
      <Modal.Body>{children}</Modal.Body>
      {footer && <Modal.Footer>{footer}</Modal.Footer>}
    </Modal>
  );
}
