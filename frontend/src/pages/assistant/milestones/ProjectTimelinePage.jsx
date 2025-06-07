// src/pages/assistant/milestones/ProjectTimelinePage.jsx

import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import apiFetch from "@/utils/apiClient";

export default function ProjectTimelinePage() {
  const { projectId } = useParams();
  const [milestones, setMilestones] = useState([]);

  useEffect(() => {
    async function fetchMilestones() {
      const data = await apiFetch(`/assistants/projects/${projectId}/milestones/`);
      setMilestones(
        data
          .filter(m => m.due_date)               // 🧹 Only milestones with due dates
          .sort((a, b) => new Date(a.due_date) - new Date(b.due_date)) // ⏳ Soonest first
      );
    }
    fetchMilestones();
  }, [projectId]);

  if (!milestones.length) return <div className="container my-5">No upcoming milestones.</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-4">🕰️ Project Timeline</h1>

      <div className="list-group">
        {milestones.map((milestone, index) => (
          <Link
            key={milestone.id}
            to={`/projects/${projectId}/milestones/${milestone.id}/edit`}
            className={`list-group-item list-group-item-action d-flex justify-content-between align-items-center ${
              index === 0 ? "list-group-item-primary" : ""
            }`}
          >
            <div>
              <h5 className="mb-1">{milestone.title}</h5>
              <small className="text-muted">
                Due {milestone.due_date ? new Date(milestone.due_date).toLocaleDateString() : "Soon"}
              </small>
            </div>
            <span className={`badge bg-${statusToColor(milestone.status)} rounded-pill`}>
              {statusLabel(milestone.status)}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}

function statusToColor(status) {
  switch (status) {
    case "completed":
      return "success";
    case "in-progress":
      return "primary";
    case "pending":
    default:
      return "secondary";
  }
}

function statusLabel(status) {
  if (status === "in-progress") return "In Progress";
  if (status === "completed") return "Completed";
  return "Pending";
}