// src/components/memory/MemoryFeedbackModal.jsx
import { useState } from "react";
import { Modal, Button, Form } from "react-bootstrap";
import { toast } from "react-toastify";

export default function MemoryFeedbackModal({ memoryId, show, onHide, onSubmitted }) {
  const [comment, setComment] = useState("");
  const [context, setContext] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSubmit = async () => {
    if (!comment.trim()) {
      toast.error("Feedback comment is required");
      return;
    }
    setSaving(true);
    try {
      const res = await fetch(`/api/memory/${memoryId}/feedback/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ comment, context }),
      });
      if (res.ok) {
        toast.success("✅ Feedback submitted");
        setComment("");
        setContext("");
        onSubmitted && onSubmitted();
        onHide();
      } else {
        toast.error("❌ Failed to submit feedback");
      }
    } catch (err) {
      console.error("Feedback error:", err);
      toast.error("❌ Server error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>🧠 Suggest Memory Feedback</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form.Group className="mb-3">
          <Form.Label>Feedback Comment</Form.Label>
          <Form.Control
            as="textarea"
            rows={3}
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="e.g. 'Use fire instead of cool'"
          />
        </Form.Group>
        <Form.Group>
          <Form.Label>Optional Context</Form.Label>
          <Form.Control
            type="text"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="e.g. 'Nicolas uses fire a lot in chats'"
          />
        </Form.Group>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>Cancel</Button>
        <Button variant="primary" onClick={handleSubmit} disabled={saving}>
          {saving ? "Submitting..." : "Submit Feedback"}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
