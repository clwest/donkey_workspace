import { useState } from "react";

export default function AssistantThinkButton({ slug, onThought }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleClick() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/assistants/${slug}/think/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "__think__" }),
      });

      if (!res.ok) throw new Error("Failed to generate thought");
      const data = await res.json();

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