import { useState } from "react";
import { Modal, Button } from "react-bootstrap";
import apiFetch from "../../utils/apiClient";

export default function MythMergeModal({ show, onHide, mythA, mythB }) {
  const [summary, setSummary] = useState("");

  const handleSubmit = async () => {
    try {
      await apiFetch("/assistants/myth-merge/", {
        method: "POST",
        body: {
          initiator: mythA.assistant,
          target_assistant: mythB.assistant,
          proposed_summary: summary,
        },
      });
      onHide();
    } catch (err) {
      console.error("Merge failed", err);
    }
  };

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>Merge Myth Layers</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div className="mb-3">
          <h6>Myth A</h6>
          <pre className="p-2 border">{mythA.summary}</pre>
        </div>
        <div className="mb-3">
          <h6>Myth B</h6>
          <pre className="p-2 border">{mythB.summary}</pre>
        </div>
        <textarea
          className="form-control"
          rows="4"
          placeholder="Proposed merged summary"
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
        />
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSubmit} disabled={!summary}>
          Propose Merge
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
