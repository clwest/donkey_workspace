import { useState } from "react";
import { Modal, Button } from "react-bootstrap";
import apiFetch from "@/utils/apiClient";

export default function FeedbackWidget({ assistantSlug = "" }) {
  const [show, setShow] = useState(false);
  const [category, setCategory] = useState("idea");
  const [description, setDescription] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState(null);

  const open = () => {
    setShow(true);
    setSent(false);
    setDescription("");
  };

  const handleSubmit = async () => {
    try {
      await apiFetch("/feedback/", {
        method: "POST",
        body: { assistant_slug: assistantSlug, category, description },
      });
      setSent(true);
    } catch {
      setError("Failed to submit");
    }
  };

  return (
    <>
      <button id="feedback-button" className="btn btn-warning btn-sm" onClick={open}>
        📝 Feedback
      </button>
      <Modal show={show} onHide={() => setShow(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Send Feedback</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {sent ? (
            <p>Thanks for your feedback!</p>
          ) : (
            <>
              <div className="mb-2">
                <select
                  className="form-select"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                >
                  <option value="bug">Bug</option>
                  <option value="idea">Idea</option>
                </select>
              </div>
              <textarea
                className="form-control"
                rows="3"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
              {error && <p className="text-danger mt-2">{error}</p>}
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShow(false)}>
            Close
          </Button>
          {!sent && (
            <Button variant="primary" onClick={handleSubmit} disabled={!description}>
              Submit
            </Button>
          )}
        </Modal.Footer>
      </Modal>
    </>
  );
}
