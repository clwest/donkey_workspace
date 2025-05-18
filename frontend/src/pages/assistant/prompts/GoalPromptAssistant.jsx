// frontend/pages/prompts/GoalPromptAssistant.jsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

export default function GoalPromptAssistant() {
  const navigate = useNavigate();
  const [goal, setGoal] = useState("");
  const [audience, setAudience] = useState("");
  const [tone, setTone] = useState("casual");
  const [keyPoints, setKeyPoints] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleGeneratePrompt() {
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/api/prompts/generate-from-idea/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          goal,
          audience,
          tone,
          key_points: keyPoints,
        }),
      });

      const data = await res.json();
      if (res.ok) {
        setResult(data.prompt);
        toast.success("✅ Prompt generated!");
      } else {
        toast.error("❌ Failed to generate prompt.");
      }
    } catch (err) {
      console.error("Error generating prompt", err);
      toast.error("❌ Error generating prompt.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">🎯 Prompt Creation Assistant</h1>

      <div className="mb-3">
        <label className="form-label">What are you trying to write?</label>
        <input
          type="text"
          className="form-control"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="e.g., A resume for a marketing job"
        />
      </div>

      <div className="mb-3">
        <label className="form-label">Who is your audience?</label>
        <input
          type="text"
          className="form-control"
          value={audience}
          onChange={(e) => setAudience(e.target.value)}
          placeholder="e.g., HR managers, casual blog readers"
        />
      </div>

      <div className="mb-3">
        <label className="form-label">Preferred Tone</label>
        <select
          className="form-select"
          value={tone}
          onChange={(e) => setTone(e.target.value)}
        >
          <option value="casual">Casual</option>
          <option value="professional">Professional</option>
          <option value="inspirational">Inspirational</option>
          <option value="funny">Funny</option>
        </select>
      </div>

      <div className="mb-3">
        <label className="form-label">Key points or content ideas</label>
        <textarea
          className="form-control"
          rows={3}
          value={keyPoints}
          onChange={(e) => setKeyPoints(e.target.value)}
          placeholder="e.g., Grew up on a farm, love robotics, want to help people"
        ></textarea>
      </div>

      <button
        className="btn btn-primary mb-4"
        disabled={loading || !goal}
        onClick={handleGeneratePrompt}
      >
        {loading ? "Generating..." : "Generate Prompt"}
      </button>

      {result && (
        <div className="bg-light border p-3 rounded">
          <h5 className="mb-2">🧠 Your Generated Prompt</h5>
          <pre>{result}</pre>
          <button
            className="btn btn-outline-success mt-3"
            onClick={() => navigate("/prompts/create", { state: { content: result } })}
          >
            ✍️ Use This Prompt
          </button>
        </div>
      )}
    </div>
  );
}
