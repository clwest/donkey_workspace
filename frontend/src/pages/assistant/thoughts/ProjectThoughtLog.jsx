// src/pages/assistant/thoughts/ProjectThoughtLog.jsx

import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import ThoughtsPanel from "../../../components/assistant/thoughts/ThoughtsPanel";
import { toast } from "react-toastify";
import ProjectRolesRow from "../../../components/assistant/roles/ProjectRolesRow";
import apiFetch from "../../../utils/apiClient";

export default function ProjectThoughtLog() {
  const { id } = useParams();
  const [thoughts, setThoughts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterAssistant, setFilterAssistant] = useState("");
  const [roles, setRoles] = useState([]);

  useEffect(() => {
    fetchThoughts();
    apiFetch(`/assistants/projects/${id}/roles/`).then(setRoles);
  }, [id, filterAssistant]);

  async function fetchThoughts() {
    try {
      setLoading(true);
      let url = `/assistants/projects/${id}/thoughts/`;
      if (filterAssistant) url += `?assistant_id=${filterAssistant}`;
      const data = await apiFetch(url);
      setThoughts(data);
    } catch (err) {
      console.error("Failed to load thoughts", err);
      toast.error("❌ Failed to load thoughts");
    } finally {
      setLoading(false);
    }
  }

  async function handleAdd(thoughtText) {
    try {
      const data = await apiFetch(`/assistants/projects/${id}/thoughts/`, {
        method: "POST",
        body: { thought: thoughtText },
      });
      setThoughts(prev => [data, ...prev]);
    } catch (err) {
      toast.error("❌ Failed to add thought");
    }
  }

  async function handleUpdate(thoughtId, newText) {
    try {
      const data = await apiFetch(`/assistants/projects/${id}/thoughts/${thoughtId}/`, {
        method: "PATCH",
        body: { thought: newText },
      });
      setThoughts(prev =>
        prev.map(t => (t.thought_id === thoughtId ? { ...t, thought: data.updated_text } : t))
      );
    } catch (err) {
      toast.error("❌ Failed to update thought");
    }
  }

  async function handleDelete(thoughtId) {
    try {
      await apiFetch(`/assistants/projects/${id}/thoughts/${thoughtId}/`, { method: "DELETE" });
      setThoughts(prev => prev.filter(t => t.thought_id !== thoughtId));
    } catch (err) {
      toast.error("❌ Failed to delete thought");
    }
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">🧠 Project Thought Log</h1>
      <ProjectRolesRow projectId={id} />
      <div className="mb-3">
        <select
          className="form-select w-auto"
          value={filterAssistant}
          onChange={(e) => setFilterAssistant(e.target.value)}
        >
          <option value="">All assistants</option>
          {roles.map((r) => (
            <option key={r.id} value={r.assistant}>
              {r.assistant_name}
            </option>
          ))}
        </select>
      </div>
      <ThoughtsPanel
        thoughts={thoughts}
        loading={loading}
        onAdd={handleAdd}
        onUpdate={handleUpdate}
        onDelete={handleDelete}
      />
      <Link to={`/assistants/projects/${id}`} className="btn btn-outline-secondary mt-4">
        🔙 Back to Project
      </Link>
    </div>
  );
}
