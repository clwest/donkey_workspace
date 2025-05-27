import { useState } from "react";
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";

export default function PromptIdeaGenerator({ onGenerate }) {
  const [idea, setIdea] = useState("");
  const [audience, setAudience] = useState("");
  const [tone, setTone] = useState("neutral");
  const [keyPoints, setKeyPoints] = useState("");
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!idea.trim()) return;
    setLoading(true);
    try {
      const data = await apiFetch(`/prompts/generate-from-idea/`, {
        method: "POST",
        body: {
          goal: idea,
          audience,
          tone,
          key_points: keyPoints,
        },
      });

      if (data && data.slug) {
        onGenerate?.(data); // Pass the full prompt object directly
        toast.success("✅ Prompt generated!");
      } else {
        toast.error("❌ Failed to generate prompt.");
      }
    } catch (err) {
      console.error("Prompt generation failed:", err);
      toast.error("❌ Server error.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-3">
      <label className="form-label">🪄 Generate Prompt from Idea</label>
      <div className="input-group mb-2">
        <input
          type="text"
          className="form-control"
          placeholder="e.g. Build a startup agent that mentors junior developers"
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
        />
      </div>

      <div className="input-group mb-2">
        <input
          type="text"
          className="form-control"
          placeholder="Audience"
          value={audience}
          onChange={(e) => setAudience(e.target.value)}
        />
      </div>

      <div className="input-group mb-2">
        <select
          className="form-select"
          value={tone}
          onChange={(e) => setTone(e.target.value)}
        >
          <option value="neutral">Neutral</option>
          <option value="professional">Professional</option>
          <option value="casual">Casual</option>
          <option value="playful">Playful</option>
        </select>
      </div>

      <div className="input-group mb-3">
        <textarea
          className="form-control"
          placeholder="Key points (optional)"
          rows={2}
          value={keyPoints}
          onChange={(e) => setKeyPoints(e.target.value)}
        />
      </div>

      <button
        className="btn btn-outline-primary"
        type="button"
        disabled={loading}
        onClick={handleGenerate}
      >
        {loading ? "Generating..." : "Generate"}
      </button>
    </div>
  );
}
