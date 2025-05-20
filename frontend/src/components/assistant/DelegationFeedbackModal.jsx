import { useState } from "react";
import Modal from "../CommonModal";
import apiFetch from "../../utils/apiClient";
import { toast } from "react-toastify";

export default function DelegationFeedbackModal({ eventId, show, onClose }) {
  const [score, setScore] = useState(3);
  const [trust, setTrust] = useState("neutral");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await apiFetch(`/assistants/delegation/${eventId}/feedback/`, {
        method: "POST",
        body: { score, trust_label: trust, notes },
      });
      toast.success("Feedback submitted");
      onClose();
    } catch (err) {
      console.error(err);
      toast.error("Failed to submit feedback");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal show={show} onClose={onClose} title="Rate This Agent">
      <div className="mb-2">
        <label className="form-label">Score (1-5)</label>
        <input
          type="number"
          min="1"
          max="5"
          className="form-control"
          value={score}
          onChange={(e) => setScore(parseInt(e.target.value) || 0)}
        />
      </div>
      <div className="mb-2">
        <label className="form-label">Trust Label</label>
        <select
          className="form-select"
          value={trust}
          onChange={(e) => setTrust(e.target.value)}
        >
          <option value="trusted">Trusted</option>
          <option value="neutral">Neutral</option>
          <option value="unreliable">Unreliable</option>
        </select>
      </div>
      <div className="mb-3">
        <label className="form-label">Notes</label>
        <textarea
          className="form-control"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>
      <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
        {loading ? "Saving..." : "Submit"}
      </button>
    </Modal>
  );
}
