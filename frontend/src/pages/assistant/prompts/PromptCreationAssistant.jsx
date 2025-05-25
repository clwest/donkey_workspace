// frontend/pages/prompts/PromptCreationAssistant.jsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { logPromptUsage } from "../../../utils/logging";

export default function PromptCreationAssistant() {
  const navigate = useNavigate();
  const [goal, setGoal] = useState("");
  const [audience, setAudience] = useState("");
  const [tone, setTone] = useState("casual");
  const [keyPoints, setKeyPoints] = useState("");
  const [keywords, setKeywords] = useState("");
  const [messyIdea, setMessyIdea] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  async function handleGeneratePrompt() {
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("/api/prompts/generate-from-idea/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          goal,
          audience,
          tone,
          key_points: `${keyPoints} ${keywords} ${messyIdea}`,
        }),
      });

      const data = await res.json();
      if (res.ok) {
        setResult(data.prompt);
        toast.success("✅ Prompt generated!");

        await logPromptUsage({
          slug: "assistant-idea-generator",
          title: "Generated via Assistant",
          context: "frontend.prompt-assistant",
          input: JSON.stringify({
            goal,
            audience,
            tone,
            keyPoints,
            keywords,
            messyIdea
          }),
          output: data.prompt,
        });

        toast.info("📚 Usage logged!");
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

  function handleSendToCreator() {
    navigate("/prompts/create", { state: { content: result } });
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">🧠 Prompt Creation Assistant</h1>

      <div className="row g-3 mb-4">
        <div className="col-md-6">
          <label className="form-label">🎯 Prompt Goal</label>
          <input
            className="form-control"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="e.g., Write a resume for introverted nurses"
          />
        </div>
        <div className="col-md-6">
          <label className="form-label">👥 Audience / Model</label>
          <input
            className="form-control"
            value={audience}
            onChange={(e) => setAudience(e.target.value)}
            placeholder="e.g., Hiring managers, GPT-4"
          />
        </div>
        <div className="col-md-4">
          <label className="form-label">🎭 Tone</label>
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
        <div className="col-md-4">
          <label className="form-label">🔑 Keywords or Constraints</label>
          <input
            className="form-control"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
          />
        </div>
        <div className="col-md-4">
          <label className="form-label">📝 Rough Idea / Draft</label>
          <input
            className="form-control"
            value={messyIdea}
            onChange={(e) => setMessyIdea(e.target.value)}
          />
        </div>
      </div>

      <div className="mb-3">
        <label className="form-label">💡 Key Points</label>
        <textarea
          className="form-control"
          rows={3}
          value={keyPoints}
          onChange={(e) => setKeyPoints(e.target.value)}
          placeholder="e.g., Ice cream, introverted donkeys, prefer night time..."
        />
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
            onClick={handleSendToCreator}
          >
            ✍️ Use This Prompt
          </button>
        </div>
      )}
    </div>
  );
}