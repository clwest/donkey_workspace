import { useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function AssistantThinkButton({ slug, onThought }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleClick() {
    setLoading(true);
    setError(null);

    try {
      const data = await apiFetch(`/assistants/${slug}/dream/`, {
        method: "POST",
      });
      if (!data) throw new Error("Failed to generate thought");
      if (onThought) onThought(data);
    } catch (err) {
      setError("Error generating thought.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="my-3">
      <button className="btn btn-secondary" onClick={handleClick} disabled={loading}>
        {loading ? "💭 Thinking..." : "🧠 Generate Thought"}
      </button>
      {error && <div className="text-danger mt-2">{error}</div>}
    </div>
  );
}