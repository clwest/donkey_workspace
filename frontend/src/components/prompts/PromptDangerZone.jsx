import { useState } from "react";
import { deletePromptWithFallback, forceDeletePrompt } from "../../hooks/useDeletePrompt";
import { useNavigate } from "react-router-dom";

export default function PromptDangerZone({ slug }) {
  const navigate = useNavigate();
  const [needsForce, setNeedsForce] = useState(false);

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this prompt?")) return;
    const result = await deletePromptWithFallback(slug);
    if (result.deleted) {
      navigate("/prompts");
    } else if (result.needsForce) {
      setNeedsForce(true);
    }
  };

  const handleForce = async () => {
    if (!window.confirm("Force delete this prompt?")) return;
    const result = await forceDeletePrompt(slug);
    if (result.deleted) {
      navigate("/prompts");
    }
    setNeedsForce(false);
  };

  return (
    <div className="mt-4 border-top pt-3">
      <h5 className="text-danger mb-2">Delete Prompt</h5>
      <button className="btn btn-danger" onClick={handleDelete}>
        Delete Prompt
      </button>
      {needsForce && (
        <div className="mt-2 alert alert-warning">
          <p className="mb-2">This prompt is linked to assistants or has mutation history.</p>
          <button className="btn btn-outline-danger" onClick={handleForce}>
            Force Delete Anyway
          </button>
        </div>
      )}
    </div>
  );
}
