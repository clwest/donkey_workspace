import { useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function TrailMilestoneEditor({ marker, onSaved }) {
  const [userNote, setUserNote] = useState(marker.user_note || "");
  const [userEmotion, setUserEmotion] = useState(marker.user_emotion || "");
  const [isStarred, setIsStarred] = useState(marker.is_starred || false);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    try {
      await apiFetch(`/trail/${marker.id}/`, {
        method: "PATCH",
        body: {
          user_note: userNote,
          user_emotion: userEmotion,
          is_starred: isStarred,
        },
      });
      onSaved && onSaved({
        user_note: userNote,
        user_emotion: userEmotion,
        is_starred: isStarred,
      });
    } catch {
      alert("Failed to save milestone");
    }
    setSaving(false);
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-3">
        <label className="form-label">Note</label>
        <textarea
          className="form-control"
          value={userNote}
          onChange={(e) => setUserNote(e.target.value)}
        />
      </div>
      <div className="mb-3">
        <label className="form-label">Emotion</label>
        <input
          className="form-control"
          value={userEmotion}
          onChange={(e) => setUserEmotion(e.target.value)}
          placeholder="😊"
        />
      </div>
      <div className="form-check mb-3">
        <input
          type="checkbox"
          id="starred-toggle"
          className="form-check-input"
          checked={isStarred}
          onChange={(e) => setIsStarred(e.target.checked)}
        />
        <label className="form-check-label" htmlFor="starred-toggle">
          Starred
        </label>
      </div>
      <button type="submit" className="btn btn-primary" disabled={saving}>
        Save
      </button>
    </form>
  );
}
