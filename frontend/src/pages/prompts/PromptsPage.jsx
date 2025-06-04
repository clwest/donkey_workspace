// frontend/pages/prompts/PromptsPage.jsx

import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./styles/PromptsPage.css";
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";
import {
  deletePromptWithFallback,
  forceDeletePrompt,
} from "../../hooks/useDeletePrompt";

export default function PromptsPage() {
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortByTokens, setSortByTokens] = useState(false);
  const [useSimilarity, setUseSimilarity] = useState(false);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [sourceFilter, setSourceFilter] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
      const fetchPrompts = async () => {
        setLoading(true);
        setError(null);
        try {
        if (useSimilarity) {
          const body = {
            text: search || "assistant",
            target: "prompt",
            top_k: 20,
          };
          const data = await apiFetch("/embeddings/search/", {
            
            method: "POST",
            body,
          });
          const promptList = data.results || data;
          console.log(promptList)
          setPrompts(Array.isArray(promptList) ? promptList : []);
        } else {
          const params = { show_all: true };
          if (sortByTokens) params.sort = "tokens";
          if (search) params.q = search;
          if (typeFilter) params.type = typeFilter;
          if (sourceFilter) params.source = sourceFilter;
          const data = await apiFetch("/prompts/", { params });
          console.log(data)
          const promptList = data.results || data;
          console.log(params)
          setPrompts(Array.isArray(promptList) ? promptList : []);
        }
        } catch (err) {
          console.error("Error loading prompts:", err);
          toast.error("❌ Failed to load prompts.");
          setError("Failed to load prompts.");
        } finally {
          setLoading(false);
        }
      };

    fetchPrompts();
  }, [search, sortByTokens, typeFilter, sourceFilter, useSimilarity]);

  function exportPrompt(prompt, format) {
    const filenameBase = (prompt.slug || prompt.title.replace(/\s+/g, "_"));
    let content = "";
    let mime = "text/plain";
  
    switch (format) {
      case "md":
        mime = "text/markdown";
        content = `---\n` +
          `title: "${prompt.title}"\n` +
          `type: ${prompt.type}\n` +
          `source: ${prompt.source}\n` +
          `tokens: ${prompt.token_count ?? "n/a"}\n` +
          `tags: [${(prompt.tags || []).map((t) => `"${t}"`).join(", ")}]\n` +
          `---\n\n${prompt.content}`;
        break;
  
      case "txt":
        content = `${prompt.title}\n\n${prompt.content}`;
        break;
  
      case "json":
        mime = "application/json";
        content = JSON.stringify(prompt, null, 2);
        break;
  
      case "csv":
        mime = "text/csv";
        content = `title,type,source,tokens,tags,content\n` +
          `"${prompt.title}","${prompt.type}","${prompt.source}",` +
          `"${prompt.token_count ?? ""}","${(prompt.tags || []).join(" | ")}","${prompt.content.replace(/"/g, '""')}"`
        break;
  
      default:
        return;
    }
  
    const blob = new Blob([content], { type: mime });
    console.log(blob)
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${filenameBase}.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="mb-0">Prompt Explorer</h1>
        <Link to="/prompts/create">
          ➕ Create New Prompt
        </Link>

        <div className="form-check form-switch">
          <input
            type="checkbox"
            className="form-check-input"
            id="sortTokens"
            checked={sortByTokens}
            onChange={(e) => setSortByTokens(e.target.checked)}
            disabled={useSimilarity}
          />
          <label className="form-check-label ms-2" htmlFor="sortTokens">
            Sort by Token Count
          </label>
        </div>
        <div className="form-check form-switch ms-3">
          <input
            type="checkbox"
            className="form-check-input"
            id="useSimilarity"
            checked={useSimilarity}
            onChange={(e) => setUseSimilarity(e.target.checked)}
          />
          <label className="form-check-label ms-2" htmlFor="useSimilarity">
            Similarity Search
          </label>
        </div>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-md-6">
          <input
            type="text"
            className="form-control"
            placeholder="Search prompts..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="col-md-3">
          <select
            className="form-select"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            disabled={useSimilarity}
          >
            <option value="">All Types</option>
            <option value="system">System</option>
            <option value="user">User</option>
            <option value="assistant">Assistant</option>
          </select>
        </div>
        <div className="col-md-3">
          <input
            type="text"
            className="form-control"
            placeholder="Filter by Source..."
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
            disabled={useSimilarity}
          />
        </div>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center my-5">
          <div className="spinner-border text-primary" />
          <p className="mt-2">Loading prompts...</p>
        </div>
      ) : prompts.length === 0 ? (
        <p className="text-center text-muted">No prompts found.</p>
      ) : (
        <div className="prompts-grid">
          {prompts.map((prompt) => (
            <div
        key={prompt.slug}
        className="prompt-card"
        onClick={() => navigate(`/prompts/${prompt.slug}`)}
      >
        <div className="prompt-title fw-bold">{prompt.title}</div>
        <div className="prompt-meta text-muted small mb-2">
          Type: {prompt.type} | Source: {prompt.source}
        </div>
        <div className="prompt-summary mb-3">
          {prompt.summary || prompt.content.slice(0, 100) + "..."}
        </div>

        <div className="dropdown text-center">
          <button
            className="btn btn-outline-primary btn-sm dropdown-toggle"
            type="button"
            id={`exportDropdown-${prompt.slug}`}
            data-bs-toggle="dropdown"
            aria-expanded="false"
            onClick={(e) => e.stopPropagation()} // Prevent navigation
          >
            Export
          </button>
          <ul className="dropdown-menu" aria-labelledby={`exportDropdown-${prompt.slug}`}>
            <li>
              <button className="dropdown-item" onClick={(e) => { e.stopPropagation(); exportPrompt(prompt, "md"); }}>
                📦 Markdown (.md)
              </button>
            </li>
            <li>
              <button className="dropdown-item" onClick={(e) => { e.stopPropagation(); exportPrompt(prompt, "txt"); }}>
                📄 Plain Text (.txt)
              </button>
            </li>
            <li>
              <button className="dropdown-item" onClick={(e) => { e.stopPropagation(); exportPrompt(prompt, "json"); }}>
                🧠 JSON (.json)
              </button>
            </li>
            <li>
              <button className="dropdown-item" onClick={(e) => { e.stopPropagation(); exportPrompt(prompt, "csv"); }}>
                📊 CSV (.csv)
              </button>
            </li>
          </ul>
          <div className="mt-2">
            <Link
              to={`/prompts/${prompt.slug}/edit`}
              className="btn btn-sm btn-outline-secondary me-2"
              onClick={(e) => e.stopPropagation()}
            >
              ✏️ Edit
            </Link>
            <button
              className="btn btn-sm btn-outline-danger"
              onClick={async (e) => {
                e.stopPropagation();
                if (!window.confirm("Delete this prompt?")) return;
                const result = await deletePromptWithFallback(prompt.slug);
                if (result.deleted) {
                  setPrompts((prev) => prev.filter((p) => p.slug !== prompt.slug));
                } else if (result.needsForce) {
                  if (window.confirm("Prompt is in use. Force delete anyway?")) {
                    const forced = await forceDeletePrompt(prompt.slug);
                    if (forced.deleted) {
                      setPrompts((prev) =>
                        prev.filter((p) => p.slug !== prompt.slug)
                      );
                    }
                  }
                }
              }}
            >
              🗑️ Delete
            </button>
          </div>
          <button
              className="btn btn-info m-3"
              onClick={(e) => {
                e.stopPropagation();
                navigator.clipboard.writeText(prompt.content);
                toast.success("📋 Prompt copied to clipboard!");
              }}
            >
              📋 Copy Prompt
            </button>
        </div>
      </div>
          ))}
        </div>
      )}
    </div>
  );
}
