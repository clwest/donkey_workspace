// frontend/pages/prompts/EditPromptPage.jsx

import { useState, useEffect } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import { toast } from "react-toastify";
import PromptIdeaGenerator from "../../components/prompts/PromptIdeaGenerator";
import apiFetch from "../../utils/apiClient";
export default function EditPromptPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { slug } = useParams();
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

  useEffect(() => {
    async function fetchPrompt() {
      try {
        const data = await apiFetch(`/prompts/${slug}/`);
        setTitle(data.title);
        setContent(data.content);
        setType(data.type);
        setSource(data.source);
        setTags((data.tags || []).join(','));
        setTokens(data.token_count || 0);
      } catch (err) {
        console.error('Failed to load prompt', err);
      }
    }
    if (slug) fetchPrompt();
  }, [slug]);

  const handleTokenCount = async (text) => {
    if (!text || !text.trim()) return; // 💡 guard clause

    try {
      const data = await apiFetch("/prompts/analyze/", {
        method: "POST",
        body: { text },
      });
      setTokens(data.tokens || 0);
    } catch (err) {
      console.error("❌ Error analyzing prompt tokens:", err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const data = await apiFetch(`/prompts/${slug}/update/`, {
        method: "PATCH",
        body: {
          title,
          content,
          type,
          source,
          tags: tags.split(",").map((t) => t.trim()),
          token_count: tokens,
          is_draft: isDraft,
        },
      });
      if (data && data.slug) {
        toast.success("✅ Prompt updated!");
        navigate(`/prompts/${data.slug}`);
      } else {
        toast.error("❌ Failed to update prompt.");
      }
    } catch (err) {
      toast.error("❌ Server error while saving.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container my-5">
      <h2>Edit Prompt</h2>

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
