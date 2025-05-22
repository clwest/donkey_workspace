import { useState, useEffect } from "react";
import PropTypes from "prop-types";

export default function AssistantPromptPanel({ projectId }) {
  const [linkedPrompts, setLinkedPrompts] = useState([]);
  const [availablePrompts, setAvailablePrompts] = useState([]);
  const [selectedPromptId, setSelectedPromptId] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [linkedRes, availableRes] = await Promise.all([
          fetch(`http://localhost:8000/api/assistants/projects/${projectId}/linked_prompts/`),
          fetch(`http://localhost:8000/api/prompts/?show_all=true`),
        ]);

        const linkedData = await linkedRes.json();
        const availableData = await availableRes.json();

        setLinkedPrompts(linkedData);
        setAvailablePrompts(availableData);
      } catch (error) {
        console.error("Error loading prompts:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [projectId]);

  async function handleLinkPrompt() {
    if (!selectedPromptId) return;

    try {
      await fetch(`http://localhost:8000/api/assistants/projects/link_prompt/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId,
          prompt_id: selectedPromptId,
        }),
      });
      window.location.reload(); // simple reload for now
    } catch (error) {
      console.error("Error linking prompt:", error);
    }
  }

  if (loading) return <div>Loading prompt links...</div>;

  return (
    <div className="mt-5">
      <h4 className="mb-3">🧠 Linked Prompts</h4>

      {linkedPrompts.length === 0 ? (
        <p className="text-muted">No prompts linked yet.</p>
      ) : (
        <ul className="list-group mb-4">
          {linkedPrompts.map((link, idx) => (
            <li key={link.id ? `link-${link.id}` : `fallback-${idx}`} className="list-group-item">
              {link.prompt?.title || <em>Unnamed Prompt</em>}
            </li>
          ))}
        </ul>
      )}

      <h6 className="mt-4">➕ Link New Prompt</h6>
      <div className="d-flex gap-2 align-items-center mt-2">
        <select
          className="form-select"
          value={selectedPromptId}
          onChange={(e) => setSelectedPromptId(e.target.value)}
          style={{ maxWidth: "400px" }}
        >
          <option value="">Select prompt...</option>
          {availablePrompts
            .filter(p => p && p.id) // optional: guard against bad API values
            .map((prompt) => (
              <option key={`prompt-${prompt.id}`} value={prompt.id}>
                {prompt.title ? prompt.title.slice(0, 50) : "Untitled"}
              </option>
          ))}
        </select>

        <button className="btn btn-primary" onClick={handleLinkPrompt}>
          🔗 Link
        </button>
      </div>
    </div>
  );
}

AssistantPromptPanel.propTypes = {
  projectId: PropTypes.string.isRequired,
};
