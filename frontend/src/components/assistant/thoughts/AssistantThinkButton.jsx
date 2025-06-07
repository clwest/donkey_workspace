import { useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function AssistantThinkButton({ projectId, onThought }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleClick() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch(
        `/assistants/projects/${projectId}/thoughts/generate/`,
        {
          method: "POST",
          body: { message: "__think__" },
        }
      );

      if (onThought) {
        // Add role tag for CoT + classification
        onThought({ ...data.reply, role: "assistant" });
      }
    } catch (err) {
      setError("Error generating thought.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="my-3">
      <button
        className="btn btn-secondary"
        onClick={handleClick}
        disabled={loading}
      >
        {loading ? "🤔 Thinking..." : "🧠 Generate Thought"}
      </button>
      {error && <div className="text-danger mt-2">{error}</div>}
    </div>
  );
}