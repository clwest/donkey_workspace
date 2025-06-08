import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import apiFetch from "@/utils/apiClient";

export default function NurturePanel({ assistant }) {
  const navigate = useNavigate();
  const [dismissed, setDismissed] = useState(
    localStorage.getItem(`nurtureDismiss-${assistant.slug}`) === "dismiss"
  );
  if (!assistant?.is_demo_clone || dismissed) return null;
  const recs = assistant.nurture_recommendations || [];
  const mentor = assistant.mentor_assistant;

  const handleStart = async () => {
    try {
      await apiFetch(`/assistants/${assistant.slug}/start_nurture/`, { method: "POST" });
      setDismissed(true);
      localStorage.setItem(`nurtureDismiss-${assistant.slug}`, "dismiss");
    } catch (e) {
      console.error(e);
    }
  };
  const remindLater = () => {
    setDismissed(true);
    localStorage.setItem(`nurtureDismiss-${assistant.slug}`, "remind");
  };
  if (dismissed) return null;
  return (
    <div className="alert alert-success mt-3">
      {mentor && (
        <p className="mb-2">
          ⭐ Mentor Assistant: {" "}
          <Link to={`/assistants/${mentor.slug}`}>{mentor.name}</Link>
        </p>
      )}
      <p className="mb-1">Suggested actions:</p>
      <div className="d-flex flex-column gap-2 mb-2">
        {recs.includes("reflect_birth") && (
          <button
            className="btn btn-sm btn-outline-primary"
            onClick={() => navigate(`/assistants/${assistant.slug}/reflect`)}
          >
            ✍️ Reflect on Birth
          </button>
        )}
        {recs.includes("create_first_objective") && (
          <button
            className="btn btn-sm btn-outline-success"
            onClick={() => navigate(`/assistants/${assistant.slug}/projects`)}
          >
            🎯 Create First Objective
          </button>
        )}
        {recs.includes("start_memory_chain") && (
          <button
            className="btn btn-sm btn-outline-warning"
            onClick={() => navigate(`/assistants/${assistant.slug}/memories`)}
          >
            📘 Start Memory Chain
          </button>
        )}
      </div>
      <div className="d-flex gap-2">
        <button className="btn btn-primary" onClick={handleStart}>
          Start Nurture
        </button>
        <button className="btn btn-outline-secondary" onClick={remindLater}>
          Remind Me Later
        </button>
        <button
          className="btn btn-link text-decoration-none"
          onClick={() => {
            setDismissed(true);
            localStorage.setItem(`nurtureDismiss-${assistant.slug}`, "dismiss");
          }}
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}
