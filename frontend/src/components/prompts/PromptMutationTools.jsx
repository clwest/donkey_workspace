import { useState } from "react";

export default function PromptMutationTools({ original, onApply, reanalyze }) {
  const [mode, setMode] = useState("clarify");
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
      const res = await fetch("http://localhost:8000/api/prompts/mutate-prompt/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: original, mode }),
      });

      const data = await res.json();
      if (res.ok) {
        setPreview(data.result);
      } else {
        alert(`Mutation failed: ${data.error || "Try another mode"}`);
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
          value={mode}
          onChange={(e) => setMode(e.target.value)}
        >
          {MODES.map((m) => (
            <option key={m} value={m}>
              {m.charAt(0).toUpperCase() + m.slice(1)}
            </option>
          ))}
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