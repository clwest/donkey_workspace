import { useState } from "react";
import Modal from "../CommonModal";

export default function DemoFeedbackModal({ show, onClose, onSubmit }) {
  const [rating, setRating] = useState(5);
  const [text, setText] = useState("");

  const handleSubmit = () => {
    onSubmit && onSubmit(rating, text);
    onClose();
  };

  return (
    <Modal show={show} onClose={onClose} title="Was this helpful?">
      <div className="mb-2">
        <label className="form-label">Rating (1-5)</label>
        <input
          type="number"
          min="1"
          max="5"
          className="form-control"
          value={rating}
          onChange={(e) => setRating(parseInt(e.target.value) || 0)}
        />
      </div>
      <div className="mb-3">
        <label className="form-label">What would make it better?</label>
        <textarea
          className="form-control"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
      </div>
      <button className="btn btn-primary" onClick={handleSubmit}>
        Submit
      </button>
    </Modal>
  );
}
