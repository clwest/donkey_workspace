import { useState } from "react";
import Modal from "../CommonModal";
import { planProjectFromMemory } from "../../api/assistants";
import { useNavigate } from "react-router-dom";

export default function PlanProjectFromMemoryModal({ slug, memoryIds, show, onClose }) {
  const [title, setTitle] = useState("");
  const [style, setStyle] = useState("bullet");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handlePlan() {
    setLoading(true);
    try {
      const res = await planProjectFromMemory(slug, {
        memory_ids: memoryIds,
        project_title: title,
        planning_style: style,
      });
      onClose();
      navigate(`/assistants/projects/${res.project_id}/mission`);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  }

  return (
    <Modal show={show} onClose={() => onClose()} title="Plan Project From Memory">
      <div className="mb-3">
        <label className="form-label">Project Title</label>
        <input
          className="form-control"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Optional title"
        />
      </div>
      <div className="mb-3">
        <label className="form-label">Planning Style</label>
        <select
          className="form-select"
          value={style}
          onChange={(e) => setStyle(e.target.value)}
        >
          <option value="bullet">Bullet</option>
          <option value="timeline">Timeline</option>
          <option value="goal-first">Goal First</option>
        </select>
      </div>
      <button className="btn btn-primary" onClick={handlePlan} disabled={loading}>
        {loading ? "Planning..." : "Create Project"}
      </button>
    </Modal>
  );
}
