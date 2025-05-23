import { useState } from "react";
import { createSceneDirectorFrame } from "../api/agents";

export default function SceneDirectorConsole({ sessionId, assistantId }) {
  const [notes, setNotes] = useState("");

  const saveFrame = () => {
    createSceneDirectorFrame({
      session: sessionId,
      director_assistant: assistantId,
      symbolic_adjustments: {},
      role_reassignments: {},
      final_scene_notes: notes,
    }).then(() => setNotes(""));
  };

  return (
    <div className="p-2 border rounded">
      <h5>Scene Director</h5>
      <textarea
        className="form-control mb-2"
        placeholder="Final scene notes"
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
      />
      <button className="btn btn-primary" onClick={saveFrame}>
        Save Frame
      </button>
    </div>
  );
}
