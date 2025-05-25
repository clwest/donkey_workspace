// src/components/thoughts/ThoughtsPanel.jsx

import { useState, useEffect } from "react";
import apiFetch from "../../../utils/apiClient";
import AssistantThoughtCard from "./AssistantThoughtCard";
import { toast } from "react-toastify";

export default function ThoughtsPanel({ projectId }) {
  const [thoughts, setThoughts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newThought, setNewThought] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchThoughts = async () => {
      setLoading(true);
      try {
        const data = await apiFetch(`/assistants/projects/${projectId}/thoughts/`);
        console.log("🧠 Fetched thoughts", data);
        if (Array.isArray(data)) {
          setThoughts(data);
        } else {
          console.warn("Unexpected thoughts payload", data);
          setThoughts([]);
        }
      } catch (err) {
        toast.error("❌ Failed to load thoughts.");
      } finally {
        setLoading(false);
      }
    };

    fetchThoughts();
  }, [projectId]);

  const handleAddThought = async () => {
    if (!newThought.trim()) return;
    setSaving(true);
    try {
      const data = await apiFetch(`/assistants/projects/${projectId}/thoughts/`, {
        method: "POST",
        body: { thought: newThought },
      });
      setThoughts(prev => [data, ...prev]);
      setNewThought("");
      toast.success("🧠 Thought added!");
    } catch (err) {
      toast.error("❌ Failed to save thought.");
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateThought = async (thoughtId, updatedText) => {
    try {
      const data = await apiFetch(`/assistants/projects/${projectId}/thoughts/${thoughtId}/`, {
        method: "PATCH",
        body: { thought: updatedText },
      });
      setThoughts(prev => prev.map(t => (t.id === thoughtId ? { ...t, thought: data.updated_text } : t)));
    } catch (err) {
      toast.error("❌ Failed to update thought.");
    }
  };

  const handleDeleteThought = (thoughtId) => {
    setThoughts(prev => prev.filter(t => t.id !== thoughtId));
  };

  return (
    <div>
      <div className="mb-3">
        <textarea
          className="form-control"
          rows={2}
          placeholder="Write a new thought..."
          value={newThought}
          onChange={(e) => setNewThought(e.target.value)}
        />
        <button
          className="btn btn-primary mt-2"
          onClick={handleAddThought}
          disabled={saving || !newThought.trim()}
        >
          {saving ? "Saving..." : "➕ Add Thought"}
        </button>
      </div>

      {loading ? (
        <p>Loading thoughts...</p>
      ) : thoughts.length === 0 ? (
        <p className="text-muted">No thoughts yet.</p>
      ) : (
        thoughts.map((thought) => (
         <AssistantThoughtCard
            key={thought.id}
            thought={thought}
            onUpdate={handleUpdateThought}
            onDelete={handleDeleteThought}
            onAdd={(t) => setThoughts((prev) => [t, ...prev])}
          />
        ))
      )}
    </div>
  );
}
