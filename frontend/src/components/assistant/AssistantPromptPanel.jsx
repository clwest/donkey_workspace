import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import apiFetch from "../../utils/apiClient";

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
          fetch(`http://localhost:8000/api/assistants/prompts/recent/`),

        ]);

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
      const newLink = await apiFetch(`/assistants/projects/link_prompt/`, {
        method: "POST",
        body: {
          project_id: projectId,
          prompt_id: selectedPromptId,
        },
      });
      setLinkedPrompts((prev) => [...prev, newLink]);
      setSelectedPromptId("");
    } catch (error) {
      console.error("Error linking prompt:", error);
    }
  }

  async function handleUnlinkPrompt(linkId) {
    try {
      await fetch(
        `http://localhost:8000/api/assistants/projects/unlink_prompt/${linkId}/`,
        {
          method: "DELETE",
        }
      );
      setLinkedPrompts((prev) => prev.filter((l) => l.id !== linkId));
    } catch (error) {
      console.error("Error unlinking prompt:", error);
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
            <li
              key={link.id ? `link-${link.id}` : `fallback-${idx}`}
              className="list-group-item d-flex justify-content-between align-items-center"
            >
              <span>
                {link.prompt?.title || <em>Unnamed Prompt</em>}
                {" "}
                <small className="text-muted ms-2">
                  {link.prompt?.token_count || 0} tokens
                </small>
              </span>
              <button
                className="btn btn-sm btn-outline-danger"
                onClick={() => handleUnlinkPrompt(link.id)}
              >
                Unlink
              </button>
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
