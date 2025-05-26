import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function PromptMutationTools({ original, promptId, onApply, reanalyze }) {
  const [mutationType, setMutationType] = useState("clarify");
  const [tone, setTone] = useState("neutral");
  const [preview, setPreview] = useState("");
  const [loading, setLoading] = useState(false);

  const MODES = [
    "clarify",
    "expand",
    "shorten",
    "formalize",
    "casualize",
    "convertToBulletPoints",
  ];

  async function mutatePrompt() {
    setLoading(true);
    setPreview("");

    try {
      const res = await apiFetch(`/prompts/mutate-prompt/`, {
        method: "POST",
        body: {
          text: original,
          mutation_type: mutationType,
          tone,
          prompt_id: promptId,
        },
      });

      const data = await res.json();
      if (res.ok) {
        setPreview(data.result);
      } else {
        alert(`Mutation failed: ${data.error || "Try another mutation type"}`);
      }
    } catch (err) {
      console.error("Mutation error:", err);
      alert("Could not reach mutation API");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card my-4 p-4 shadow-sm">
      <h5 className="mb-3">🔧 Prompt Mutation Tools</h5>

      <div className="d-flex gap-2 align-items-center mb-3">
        <select
          className="form-select w-auto"
          value={mutationType}
          onChange={(e) => setMutationType(e.target.value)}
        >
          {MODES.map((m) => (
            <option key={m} value={m}>
              {m.charAt(0).toUpperCase() + m.slice(1)}
            </option>
          ))}
        </select>
        <select
          className="form-select w-auto"
          value={tone}
          onChange={(e) => setTone(e.target.value)}
        >
          <option value="neutral">Neutral</option>
          <option value="professional">Professional</option>
          <option value="casual">Casual</option>
          <option value="playful">Playful</option>
        </select>
        <button
          className="btn btn-dark"
          onClick={mutatePrompt}
          disabled={loading}
        >
          {loading ? "Mutating..." : "Mutate Prompt"}
        </button>
      </div>

      {preview && (
        <div className="mt-3">
          <label className="form-label">Preview</label>
          <textarea
            className="form-control"
            rows={8}
            value={preview}
            readOnly
          />
          <button
            className="btn btn-success mt-2"
            onClick={() => {
              onApply(preview);
              if (reanalyze) reanalyze(preview);
            }}
          >
            ✅ Use This Version
          </button>
        </div>
      )}
    </div>
  );
}