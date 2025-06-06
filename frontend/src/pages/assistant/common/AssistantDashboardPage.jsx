import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import PrimaryStar from "../../../components/assistant/PrimaryStar";
import AssistantBadgeIcon from "../../../components/assistant/AssistantBadgeIcon";

const AVATAR_EMOJI = {
  owl: "🦚",
  fox: "🦊",
  robot: "🤖",
  wizard: "🧙‍♂️",
};

export default function AssistantDashboardPage() {
  const [assistants, setAssistants] = useState([]);

  useEffect(() => {
    async function fetchAssistants() {
      try {
        const data = await apiFetch("/assistants/");
        setAssistants(data);
      } catch (err) {
        console.error("Failed to fetch assistants:", err);
      }
    }
    fetchAssistants();
  }, []);

  return (
    <div className="container my-5">
      <h1 className="display-5 mb-4">🧑‍💼 Assistant Dashboard</h1>

      <div className="row g-4">
        {assistants.map((assistant) => (
          <div className="col-md-6 col-lg-4" key={assistant.id}>
            <Link
              to={
                assistant.current_project
                  ? `/assistants/projects/${assistant.current_project.id}`
                  : `/assistants/${assistant.slug}`
              }
              className="text-decoration-none"
            >
              <div className="card shadow-sm h-100">
                <div className="card-body">
                  <h5 className="card-title">
                    <span className="me-1">
                      {AVATAR_EMOJI[assistant.avatar_style] || ""}
                    </span>
                    {assistant.name}
                    <PrimaryStar isPrimary={assistant.is_primary} />
                    <AssistantBadgeIcon
                      badges={assistant.skill_badges}
                      primaryBadge={assistant.primary_badge}
                    />
                  </h5>
                  {assistant.role && (
                    <p className="small text-muted">Role: {assistant.role}</p>
                  )}
                  <p className="text-muted mb-1">{assistant.specialty}</p>
                  <p className="card-text small">
                    {assistant.description?.slice(0, 100) || "No description."}
                  </p>
                  <span
                    className={`badge ${assistant.is_active ? "bg-success" : "bg-secondary"}`}
                  >
                    {assistant.is_active ? "Active" : "Inactive"}
                  </span>
                  {assistant.needs_recovery && (
                    <span className="badge bg-warning text-dark ms-2">Misaligned</span>
                  )}
                </div>
              </div>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
