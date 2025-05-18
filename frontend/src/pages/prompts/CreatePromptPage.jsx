// frontend/pages/prompts/CreatePromptPage.jsx

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useLocation } from "react-router-dom";
import { toast } from "react-toastify";
import PromptIdeaGenerator from "../../components/prompts/PromptIdeaGenerator";
export default function CreatePromptPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [title, setTitle] = useState("");
 
  const [source, setSource] = useState("user");
  const [type, setType] = useState("system");
  const [tags, setTags] = useState("");
  const [tokens, setTokens] = useState(0);
  const [idea, setIdea] = useState("");
  const [saving, setSaving] = useState(false);
  const [isDraft, setIsDraft] = useState(false);
  const [content, setContent] = useState(location.state?.content || "");

  useEffect(() => {
    const content = location.state?.content;
    if (content && content.trim()) {
      setContent(content);
      handleTokenCount(content);

      if (!title) {
        const timestamp = new Date().toISOString().slice(0, 16).replace("T", " ");
        setTitle(`Generated Prompt – ${timestamp}`);
      }
    }
  }, [location.state]);

  const handleTokenCount = async (text) => {
    if (!text || !text.trim()) return; // 💡 guard clause

    try {
      const res = await fetch("http://localhost:8000/api/prompts/analyze/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (res.ok) {
        const data = await res.json();
        setTokens(data.tokens || 0);
      } else {
        console.warn("❌ Token analysis failed");
      }
    } catch (err) {
      console.error("❌ Error analyzing prompt tokens:", err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const response = await fetch("http://localhost:8000/api/prompts/create/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          content,
          type,
          source,
          tags: tags.split(",").map((t) => t.trim()),
          token_count: tokens,
          is_draft: isDraft,
        }),
      });
      const data = await response.json();
      if (response.ok) {
        toast.success("✅ Prompt saved!");
        navigate(`/prompts/${data.slug}`);
      } else {
        toast.error("❌ Failed to save prompt.");
      }
    } catch (err) {
      toast.error("❌ Server error while saving.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container my-5">
      <h2>Create New Prompt</h2>

      <div className="my-4">
        <label className="form-label">Have an idea?</label>
      <PromptIdeaGenerator onGenerate={(generatedPrompt) => {
        navigate(`/prompts/${generatedPrompt.slug}`);
      }} />
      </div>

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Title</label>
          <input
            type="text"
            className="form-control"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>

        <div className="mb-3">
          <label className="form-label">Prompt Content</label>
          <textarea
            className="form-control"
            rows="8"
            value={content}
            onChange={(e) => {
              setContent(e.target.value);
              handleTokenCount(e.target.value);
            }}
            required
          />
        </div>

        <div className="row mb-3">
          <div className="col-md-4">
            <label className="form-label">Type</label>
            <select
              className="form-select"
              value={type}
              onChange={(e) => setType(e.target.value)}
            >
              <option value="system">System</option>
              <option value="user">User</option>
              <option value="assistant">Assistant</option>
            </select>
          </div>

          <div className="col-md-4">
            <label className="form-label">Source</label>
            <input
              type="text"
              className="form-control"
              value={source}
              onChange={(e) => setSource(e.target.value)}
            />
          </div>

          <div className="col-md-4">
            <label className="form-label">Tags (comma-separated)</label>
            <input
              type="text"
              className="form-control"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
            />
          </div>
        </div>

        <div className="form-check mb-3">
          <input
            className="form-check-input"
            type="checkbox"
            id="draftCheck"
            checked={isDraft}
            onChange={(e) => setIsDraft(e.target.checked)}
          />
          <label className="form-check-label" htmlFor="draftCheck">
            Save as Draft
          </label>
        </div>

        <p className="text-muted">Estimated Tokens: {tokens}</p>

        <button type="submit" className="btn btn-success" disabled={saving}>
          {saving ? "Saving..." : "💾 Save Prompt"}
        </button>
      </form>
    </div>
  );
}
