import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AssistantIntelligencePanel({ projectId, assistant: propAssistant }) {
  const [activeTab, setActiveTab] = useState("thoughts");
  const [thoughts, setThoughts] = useState([]);
  const [reflections, setReflections] = useState([]);
  const [newThought, setNewThought] = useState("");
  const [autoMode, setAutoMode] = useState(true);
  const [loading, setLoading] = useState(false);
  const [reflecting, setReflecting] = useState(false);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [assistant, setAssistant] = useState(propAssistant || null);
  const [devDocs, setDevDocs] = useState([]);

  useEffect(() => {
    if (!projectId) return;
    loadContent();
    if (!propAssistant) {
      apiFetch(`/assistants/projects/${projectId}/`).then((data) => {
        setAssistant(data.assistant || null);
        setDevDocs(data.dev_docs || []);
      }).catch((err) => console.error("Failed to load project", err));
    }
  }, [projectId]);

  async function loadContent() {
    try {
      const [thoughtsRes, reflectionsRes] = await Promise.all([
        apiFetch(`/assistants/projects/${projectId}/thoughts/`),
        apiFetch(`/assistants/projects/${projectId}/reflections/`)
      ]);
      setThoughts(thoughtsRes || []);
      setReflections(reflectionsRes || []);
    } catch (err) {
      console.error("🧠 Failed to load assistant content:", err);
    }
  }

  async function handleCreateThought() {
    setLoading(true);
    try {
      const res = await apiFetch(`/assistants/projects/${projectId}/thoughts/generate/`, {
        method: "POST",
      });
      setThoughts(prev => [res, ...prev]);
    } catch (err) {
      console.error("Failed to generate thought:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveThought() {
    if (!newThought.trim()) return;
    setThoughts(prev => [
      {
        id: Date.now(),
        thought: newThought,
        created_at: new Date().toISOString(),
      },
      ...prev,
    ]);
    setNewThought("");
  }

  async function handleReflectNow() {
    setReflecting(true);
    try {
      const res = await apiFetch(`/assistants/projects/${projectId}/thoughts/reflect/`, {
        method: "POST",
      });
      setReflections(prev => [res, ...prev]);
    } catch (err) {
      console.error("Reflection failed:", err);
    } finally {
      setReflecting(false);
    }
  }

  const generateSystemPrompt = async () => {
    if (!assistant || !devDocs.length) return;
    const docId = devDocs[0].id;
    if (!docId) return;
    setLoadingDocs(true);
    try {
      const res = await apiFetch(`/intel/intelligence/bootstrap-agent/${docId}/`, {
        method: "POST",
      });
      if (res?.config) {
        const cfg = JSON.parse(res.config);
        if (cfg.system_prompt) {
          setAssistant((prev) => ({
            ...prev,
            system_prompt: { ...(prev?.system_prompt || {}), content: cfg.system_prompt },
          }));
        }
      }
    } catch (err) {
      console.error("Failed to generate prompt from docs:", err);
    } finally {
      setLoadingDocs(false);
    }
  };

  return (
    <div className="my-5">
      <h3>🧠 Assistant Intelligence Panel</h3>

      <div className="d-flex gap-3 align-items-center mb-3">
        <div className="btn-group">
          <button className={`btn btn-sm ${activeTab === "thoughts" ? "btn-primary" : "btn-outline-primary"}`} onClick={() => setActiveTab("thoughts")}>Thoughts</button>
          <button className={`btn btn-sm ${activeTab === "reflections" ? "btn-primary" : "btn-outline-primary"}`} onClick={() => setActiveTab("reflections")}>Reflections</button>
        </div>
        <div className="form-check form-switch">
          <input className="form-check-input" type="checkbox" checked={autoMode} onChange={() => setAutoMode(!autoMode)} />
          <label className="form-check-label">Auto-Reflect</label>
        </div>
      </div>
      <div className="mt-4">
        <h5>📚 Intelligence Settings</h5>
        <button onClick={generateSystemPrompt} disabled={loadingDocs} variant="info">
          {loadingDocs ? "Generating..." : "Generate System Prompt from Docs"}
        </button>
      </div>

      {activeTab === "thoughts" && (
        <div>
          <textarea
            className="form-control mb-2"
            rows="3"
            placeholder="Write a new thought..."
            value={newThought}
            onChange={(e) => setNewThought(e.target.value)}
          />
          <div className="mb-3 d-flex gap-2">
            <button className="btn btn-sm btn-success" onClick={handleSaveThought}>💾 Save Thought</button>
            <button className="btn btn-sm btn-outline-primary" onClick={handleCreateThought} disabled={loading}>
              {loading ? "Thinking..." : "🧠 Generate Thought"}
            </button>
            <button className="btn btn-sm btn-outline-info" onClick={handleReflectNow} disabled={reflecting}>
              {reflecting ? "Reflecting..." : "📘 Reflect"}
            </button>
          </div>

          {thoughts.map((t, idx) => (
            <div key={t.id || `thought-${idx}`} className="card mb-2">
              <div className="card-body">
                <p>{t.thought}</p>
                <small className="text-muted">{new Date(t.created_at).toLocaleString()}</small>
              </div>
            </div>
          ))}
        </div>
      )}
        {activeTab === "reflections" && (
        <div>
            {reflections.length === 0 ? (
            <p className="text-muted">No reflections yet.</p>
            ) : (
            reflections.map((r, idx) => (
                <div key={r.id || `reflection-${idx}`} className="card mb-2">
                <div className="card-body">
                    <div className="d-flex justify-content-between align-items-start">
                    <div>
                        <h5 className="mb-1">{r.title || "Untitled Reflection"}</h5>
                        <p className="text-muted small mb-2">
                        {r.created_at ? new Date(r.created_at).toLocaleString() : "Unknown date"}
                        </p>
                    </div>
                    {r.category && (
                        <span
                        className="badge bg-dark text-light ms-2"
                        style={{ fontSize: "0.7rem", height: "fit-content" }}
                        >
                        {r.category.toUpperCase()}
                        </span>
                    )}
                    </div>

                    <p className="mb-2">{r.summary || <em>No summary available.</em>}</p>

                        {r.steps && r.steps.length > 0 && (
                        <div className="mt-2">
                            <strong>🧩 Reasoning Steps:</strong>
                            <ul className="mb-2 ps-3">
                            {r.steps.map((step, idx) => (
                                <li key={`step-${idx}`} className="small">{step}</li>
                            ))}
                            </ul>
                        </div>
                        )}

                        <div className="d-flex justify-content-between align-items-center text-muted small mt-2">
                        <span>🤖 {r.model || "unknown model"}</span>
                        <span>⏰ {new Date(r.created_at).toLocaleString()}</span>
                        </div>

                    {r.insights && (
                    <div className="alert alert-info mt-2">
                        <strong>Insight:</strong> {r.insights}
                    </div>
                    )}
                </div>
                </div>
            ))
            )}
        </div>
        )}
    </div>
  );
}

