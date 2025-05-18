// src/components/assistant/milestones/MilestoneCard.jsx

import { useState } from "react";
import { toast } from "react-toastify";
import MilestoneStatusSelector from "./MilestoneStatusSelector";
import MilestoneStatusBadge from "./MilestoneStatusBadge";

export default function MilestoneCard({ milestone, projectId, onUpdate, onUpdateDescription }) {
  const [editingTitle, setEditingTitle] = useState(false);
  const [titleDraft, setTitleDraft] = useState(milestone.title);

  const [editingDescription, setEditingDescription] = useState(false);
  const [descriptionDraft, setDescriptionDraft] = useState(milestone.description || "");

  async function updateTitle(newTitle) {
    const res = await fetch(`http://localhost:8000/api/assistants/milestones/${milestone.id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: newTitle }),
    });
    if (res.ok) {
      const updated = await res.json();
      onUpdate(updated);
      toast.success("✅ Title updated!");
    } else {
      toast.error("❌ Failed to update title.");
    }
  }

  async function handleTitleSubmit(e) {
    e.preventDefault();
    await updateTitle(titleDraft);
    setEditingTitle(false);
  }

  async function handleDescriptionBlur() {
    if (descriptionDraft !== milestone.description) {
      await onUpdateDescription(milestone.id, descriptionDraft);
      toast.success("✅ Description updated!");
    }
    setEditingDescription(false);
  }

  return (
    <div className="card shadow-sm h-100">
      <div className="card-body d-flex flex-column">
        
        {/* Title Editable */}
        {editingTitle ? (
          <form onSubmit={handleTitleSubmit}>
            <input
              className="form-control mb-2"
              value={titleDraft}
              onChange={(e) => setTitleDraft(e.target.value)}
              onBlur={handleTitleSubmit}
              autoFocus
            />
          </form>
        ) : (
          <h5
            className="card-title"
            onDoubleClick={() => setEditingTitle(true)}
            title="Double-click to edit title"
            style={{ cursor: "pointer" }}
          >
            {milestone.title}
          </h5>
        )}

        {/* Inline Status Badge */}
        <MilestoneStatusBadge status={milestone.status} />

        {/* Description Editable */}
        {editingDescription ? (
          <textarea
            className="form-control mb-2 mt-2"
            value={descriptionDraft}
            onChange={(e) => setDescriptionDraft(e.target.value)}
            onBlur={handleDescriptionBlur}
            rows={3}
            autoFocus
          />
        ) : (
          <p
            className="card-text small text-muted mt-2"
            onDoubleClick={() => setEditingDescription(true)}
            title="Double-click to edit description"
            style={{ cursor: "pointer" }}
          >
            {milestone.description ? milestone.description.slice(0, 120) : "No description yet..."}
          </p>
        )}

        <MilestoneStatusSelector
          milestone={milestone}
          onStatusChange={(newStatus) => onUpdate({ ...milestone, status: newStatus })}
        />

        {milestone.due_date && (
          <p className="text-muted small mt-3">
            📅 Due: {new Date(milestone.due_date).toLocaleDateString()}
          </p>
        )}
      </div>
    </div>
  );
}