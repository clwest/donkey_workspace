// frontend/pages/memories/MemoryDetailPage.jsx

import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import MemoryFlagPanel from "../../../components/memory/MemoryFlagPanel";
import MemoryForkButton from "../../../components/memory/MemoryForkButton";
import TagBadge from "../../../components/TagBadge";
import { suggestDelegation } from "../../../api/assistants";
import "../styles/MemoryDetailPage.css";

export default function MemoryDetailPage() {
  const { id } = useParams();
  const [memory, setMemory] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [editMode, setEditMode] = useState(false)
  const [formData, setFormData] = useState({ title: "", event: "", emotion: "", importance: 5 });
  const navigate = useNavigate();

  async function fetchMemory() {
    const res = await fetch(`/api/memory/${id}/`);
    const data = await res.json();
    setMemory(data);
    setFormData({
      title: data.title || "",
      event: data.event || "",
      emotion: data.emotion || "",
      importance: data.importance || 5,
    });
    if (data.voice_clip) {
      const base = window.location.origin.replace(/\/$/, "");
      setAudioUrl(`${base}${data.voice_clip}`);
    }
  }

  useEffect(() => {
    fetchMemory();
  }, [id]);

  async function handleCreateProjectFromMemory() {
    const slug = memory.linked_thought?.assistant_slug;
    if (!slug) {
      console.warn("MemoryDetailPage: missing assistant slug for project creation");
      return;
    }
    const res = await fetch(`/api/assistants/${slug}/projects/from-memory/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ memory_id: id }),
    });

    if (res.ok) {
      const data = await res.json();
      navigate(`/projects/${data.project_id}`);
    } else {
      alert("Failed to create project from memory.");
    }
  }

  async function handleSuggestAgent() {
    const slug = memory.linked_thought?.assistant_slug;
    if (!slug) return;
    try {
      const data = await suggestDelegation(slug, {
        context_type: "memory",
        context_id: memory.id,
      });
      if (data.recommended_assistant) {
        alert(`Recommend: ${data.recommended_assistant.name}\nReason: ${data.recommended_assistant.reason}`);
      } else {
        alert("No suggestion available");
      }
    } catch (err) {
      alert("Failed to get recommendation");
    }
  }

  async function handleCheckSource() {
    try {
      const res = await fetch("/api/rag/check-source/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          assistant_id: memory.linked_thought?.assistant_slug || "", 
          content: memory.event,
          mode: "memory",
        }),
      });
      const data = await res.json();
      if (data.results && data.results.length > 0) {
        const top = data.results[0];
        alert(`Top match ${Math.round(top.similarity_score * 100)}%\n${top.text.slice(0,120)}...`);
      } else {
        alert("No matching source chunk found.");
      }
    } catch (err) {
      alert("Failed to check source");
    }
  }

  async function handleSaveEdit() {
    const res = await fetch(`/api/memory/${id}`, {
      method: "PATCH",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(formData),

    });

    if (res.ok) {
      const updated = await res.json();
      setMemory(updated);
      setEditMode(false);
    } else {
      alert("Failed to Save Changes")
    }
    
  }

  if (!memory) return <div className="container my-5">Loading memory...</div>;
  console.log(memory.linked_thought)

  return (
    <div className="container my-5">
      <h2 className="mb-3">🧠 {memory.title || "Memory Detail"}</h2>

      <div className="card p-4 mb-4 shadow-sm">
        {memory.parent_memory && (
          <div className="text-muted mb-2">🧬 Refined from {memory.parent_memory.slice(0,8)}</div>
        )}
        <p><strong>Event:</strong> {memory.event}</p>
        <p><strong>Timestamp:</strong> {new Date(memory.timestamp).toLocaleString()}</p>
        <p><strong>Emotion:</strong> {memory.emotion || "None"}</p>
        <p><strong>Importance:</strong> {memory.importance} / 10</p>

        {memory.flags && memory.flags.length > 0 && (
          <MemoryFlagPanel flags={memory.flags} />
        )}

        {memory.tags?.length > 0 && (
          <div className="mb-3">
            <strong>Tags:</strong>{" "}
            {memory.tags.map((tag) => (
              <TagBadge key={tag.id} tag={tag} />
            ))}
          </div>
        )}

        {audioUrl && (
          <div className="my-4">
            <h5>🎧 Voice Clip:</h5>
            <audio controls className="w-100" src={audioUrl}>
              Your browser does not support the audio element.
            </audio>
          </div>
        )}

        {memory.full_transcript && (
          <div className="bg-light border rounded p-3 mt-4">
            <h5 className="mb-2">🗣️ Full Conversation Transcript</h5>
            <div className="overflow-auto" style={{ maxHeight: "300px", whiteSpace: "pre-wrap" }}>
              {memory.full_transcript}
            </div>
          </div>
        )}

      {memory.linked_thought && (
        <div className="alert alert-light border mt-4">
          <strong>🔗 Linked Thought:</strong>
          <br />
          <Link to={`/assistants/${memory.linked_thought.assistant_slug}/thoughts/${memory.linked_thought.id}`}>
            View Full Thought
          </Link>
        </div>
      )}
      </div>
      {editMode ? (
          <div>
            <input value={formData.title} placeholder="Title" onChange={e => setFormData({ ...formData, title: e.target.value })} />
            <input value={formData.event} onChange={e => setFormData({ ...formData, event: e.target.value })} />
            <input value={formData.emotion} onChange={e => setFormData({ ...formData, emotion: e.target.value })} />
            <input type="number" value={formData.importance} onChange={e => setFormData({ ...formData, importance: e.target.value })} />
            <button onClick={handleSaveEdit}>Save</button>
            <button onClick={() => setEditMode(false)}>Cancel</button>
          </div>
        ) : (
          <div>
            <p className="fw-bold">{memory.title}</p>
            <p>{memory.event}</p>
            <p>{memory.emotion}</p>
            <p>{memory.importance}/10</p>
            <button onClick={() => setEditMode(true)}>Edit</button>
          </div>
        )}

      <div className="d-flex gap-3">
        <button className="btn btn-primary" onClick={handleCreateProjectFromMemory}>
          🚀 Create Project from Memory
        </button>
        <button className="btn btn-outline-primary" onClick={handleSuggestAgent}>
          🤖 Suggest Agent
        </button>
        <button className="btn btn-outline-info" onClick={handleCheckSource}>
          📄 Check Source
        </button>
        <MemoryForkButton
          memoryId={memory.id}
          assistantSlug={memory.linked_thought?.assistant_slug}
          onForked={fetchMemory}
        />
        {memory.is_conversation && memory.session_id && (
          <Link
            to={`/assistants/sessions/${memory.session_id}`}
            className="btn btn-outline-info"
          >
            🔍 View Full Conversation
          </Link>
        )}
        {memory.linked_thought?.assistant_slug ? (
          <Link to={`/assistants/${memory.linked_thought.assistant_slug}`} className="btn btn-outline-secondary">
            🔙 Back to Assistant
          </Link>
        ) : (
          <Link to="/memories" className="btn btn-outline-secondary">
            🔙 Back to Memories
          </Link>
        )}

      </div>

      <div className="mt-4">
        <details>
          <summary>🔮 Simulated Forks ({memory.simulated_forks?.length || 0})</summary>
          {memory.simulated_forks && memory.simulated_forks.length > 0 ? (
            memory.simulated_forks.map((fork) => (
              <div key={fork.id} className="border rounded p-2 my-2">
                {fork.hypothetical_action && (
                  <div><strong>Action:</strong> {fork.hypothetical_action}</div>
                )}
                {fork.reason_for_simulation && (
                  <div className="text-muted">{fork.reason_for_simulation}</div>
                )}
                <div className="mt-1" style={{ whiteSpace: "pre-wrap" }}>
                  {fork.simulated_outcome}
                </div>
              </div>
            ))
          ) : (
            <p className="text-muted">No simulations yet.</p>
          )}
        </details>
      </div>
    </div>
  );
}