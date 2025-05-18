// frontend/components/mcp_core/UserReflectionCard.jsx

import { Link } from "react-router-dom";
import MoodBadge from "./MoodBadge";

export default function UserReflectionCard({ reflection }) {
  if (!reflection) return null;

  return (
    <Link
      to={`/user/reflections/${reflection.id}`}
      className="list-group-item list-group-item-action"
    >
      <div className="d-flex w-100 justify-content-between">
        <h5 className="mb-1">{reflection.title || `Reflection #${reflection.id}`}</h5>
        <small className="text-muted">{reflection.created_at}</small>
      </div>
      <p className="mb-1">{reflection.summary?.slice(0, 200) || "No summary available."}...</p>
      {reflection.mood && <MoodBadge mood={reflection.mood} />}
    </Link>
  );
}