// components/prompts/AssignPromptModal.jsx
import React, { useState, useEffect } from "react";
import Modal from "../CommonModal";
import apiFetch from "../../utils/apiClient";

export default function AssignPromptModal({ promptId, show, onClose }) {
  const [assistants, setAssistants] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchAssistants() {
      const res = await apiFetch("/assistants/?limit=100");
      setAssistants(res.results);
    }
    if (show) fetchAssistants();
  }, [show]);

  async function assignPrompt() {
    if (!selected) return;
    setLoading(true);
    try {
      await apiFetch(`/api/assistants/${selected}/assign-prompt/`, {
        method: "POST",
        body: JSON.stringify({ prompt_id: promptId }),
      });
      onClose(true); // Trigger refresh
    } catch (e) {
      console.error("Failed to assign prompt:", e);
      setLoading(false);
    }
  }

  return (
    <Modal show={show} onClose={() => onClose(false)} title="Assign Prompt to Assistant">
      <div className="mb-3">
        <label>Select Assistant</label>
        <select
          className="form-select"
          value={selected || ""}
          onChange={(e) => setSelected(e.target.value)}
        >
          <option value="" disabled>
            -- Choose an assistant --
          </option>
          {assistants.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name}
            </option>
          ))}
        </select>
      </div>

      <button
        className="btn btn-primary"
        onClick={assignPrompt}
        disabled={!selected || loading}
      >
        {loading ? "Assigning..." : "Assign Prompt"}
      </button>
    </Modal>
  );
}
