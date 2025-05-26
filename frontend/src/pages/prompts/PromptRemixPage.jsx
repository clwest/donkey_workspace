// frontend/pages/prompts/PromptRemixPage.jsx

import { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";
import "./styles/PromptRemixPage.css";

export default function PromptRemixPage() {
  const { slug } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const preloadedMutation = location.state?.mutationResult;
  const preloadedMode = location.state?.mode || "clarify";

  const [originalPrompt, setOriginalPrompt] = useState(null);
  const [remixedContent, setRemixedContent] = useState(preloadedMutation || "");
  const [remixMode, setRemixMode] = useState(preloadedMode);
  const [tone, setTone] = useState("neutral");
  const [loading, setLoading] = useState(false);
  const [customTitle, setCustomTitle] = useState("");
  const [editingTitle, setEditingTitle] = useState(false);
  

  useEffect(() => {
    async function fetchPrompt() {
      try {
        const data = await apiFetch(`/prompts/${slug}/`);
        setOriginalPrompt(data);
        setCustomTitle(`Remix: ${data.title}`);

        // Set remixedContent explicitly if not already set
        if (!preloadedMutation) {
          setRemixedContent(data.content || ""); // Fallback to empty string
        }
      } catch (err) {
        console.error("Failed to load prompt:", err);
        toast.error("❌ Failed to load prompt");
      }
    }
    fetchPrompt();
  }, [slug]);

  async function handleMutate() {
    if (!remixedContent.trim()) {
      toast.warning("📝 Please enter some content to mutate.");
      return;
    }

    setLoading(true);
    try {
      const data = await apiFetch("/prompts/mutate-prompt/", {
        method: "POST",
        body: {
          text: remixedContent,
          mutation_type: remixMode,
          tone,
          prompt_id: originalPrompt?.id,
        },
      });

      setRemixedContent(data.result);
      toast.success("✅ Remix mutation complete!");
    } catch (error) {
      console.error("Error mutating prompt:", error);
      toast.error("❌ Remix failed. Try again!");
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    try {
      const data = await apiFetch("/prompts/create/", {
        method: "POST",
        body: {
          title: customTitle,
          content: remixedContent,
          source: `remix-of-${originalPrompt.source}`,
          type: "system",
          tags: [],
          token_count: remixedContent.length,
        },
      });

      toast.success("✅ Remix saved!");
      await saveMemoryEntry(customTitle, remixedContent);
      navigate(`/prompts/${data.slug}`);
    } catch (error) {
      console.error(error);
      toast.error("❌ Failed to save remix");
    }
  }

  async function saveMemoryEntry(title, content) {
    try {
      await apiFetch("/memory/save/", {
        method: "POST",
        body: {
          event: "Remix Saved",
          memory_type: "reflection",
          title,
          content,
        },
      });

      toast.info("🧠 Memory saved!");
    } catch (error) {
      console.error("Error saving memory:", error);
    }
  }

  if (!originalPrompt) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-5">
      <div className="d-flex align-items-center mb-4">
        {editingTitle ? (
          <input
            className="form-control form-control-sm"
            style={{ maxWidth: "400px" }}
            value={customTitle}
            onChange={(e) => setCustomTitle(e.target.value)}
            onBlur={() => setEditingTitle(false)}
            autoFocus
          />
        ) : (
          <>
            <h1 className="me-2">{customTitle}</h1>
            <button
              onClick={() => setEditingTitle(true)}
              className="btn btn-sm btn-outline-secondary"
              title="Edit title"
            >
              ✏️
            </button>
          </>
        )}
      </div>

      <div className="row">
        <div className="col-md-6">
          <h5>Original Prompt</h5>
          <div className="scroll-box">
            <pre>{originalPrompt.content}</pre>
          </div>
        </div>

        <div className="col-md-6">
          <h5>Remixed Prompt</h5>
          <textarea
            className="form-control"
            style={{ height: "400px", whiteSpace: "pre-wrap" }}
            value={remixedContent}
            onChange={(e) => setRemixedContent(e.target.value)}
          />
        </div>
      </div>

      <div className="d-flex justify-content-between align-items-center mt-4 flex-wrap gap-2">
        <div className="d-flex gap-2">
          <select
            className="form-select"
            style={{ width: "200px" }}
            value={remixMode}
            onChange={(e) => setRemixMode(e.target.value)}
            disabled={loading}
          >
            <option value="clarify">Clarify</option>
            <option value="expand">Expand</option>
            <option value="shorten">Shorten</option>
            <option value="formalize">Formalize</option>
            <option value="casualize">Casualize</option>
            <option value="convertToBulletPoints">Bullet Points</option>
          </select>
          <select
            className="form-select"
            style={{ width: "160px" }}
            value={tone}
            onChange={(e) => setTone(e.target.value)}
            disabled={loading}
          >
            <option value="neutral">Neutral</option>
            <option value="professional">Professional</option>
            <option value="casual">Casual</option>
            <option value="playful">Playful</option>
          </select>

          <button onClick={handleMutate} disabled={loading} className="btn btn-secondary">
            {loading ? "Mutating..." : "Mutate Prompt"}
          </button>
        </div>

        <div className="d-flex gap-2">
          <button onClick={handleSave} className="btn btn-primary">
            💾 Save Remix
          </button>
          <button onClick={() => navigate(`/prompts/${slug}`)} className="btn btn-outline-secondary">
            ↩️ Back to Prompt
          </button>
        </div>
      </div>
    </div>
  );
}
