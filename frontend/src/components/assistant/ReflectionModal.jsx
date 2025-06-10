import { useState } from "react";
import apiFetch from "../../utils/apiClient";
import { toast } from "react-toastify";
import CommonModal from "../CommonModal";

export default function ReflectionModal({ slug, show, onClose }) {
  const [content, setContent] = useState("");
  const [rating, setRating] = useState(5);

  const handleSubmit = async () => {
    try {
      await apiFetch(`/assistants/${slug}/reflect/`, {
        method: "POST",
        body: { content, rating },
      });
      toast.success("Reflection saved");
      onClose();
    } catch (err) {
      console.error(err);
      toast.error("Failed to save reflection");
    }
  };

  const footer = (
    <>
      <button className="btn btn-secondary" onClick={onClose}>
        Cancel
      </button>
      <button className="btn btn-primary" onClick={handleSubmit}>
        Save
      </button>
    </>
  );

  return (
    <CommonModal show={show} onClose={onClose} title="Reflect on Session" footer={footer}>
      <div className="mb-3">
        <textarea
          className="form-control"
          rows={4}
          placeholder="Your thoughts..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
      </div>
      <div className="mb-2">
        <label className="form-label me-2">Rating</label>
        <select
          className="form-select w-auto d-inline-block"
          value={rating}
          onChange={(e) => setRating(parseInt(e.target.value))}
        >
          {[1, 2, 3, 4, 5].map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </div>
    </CommonModal>
  );
}
