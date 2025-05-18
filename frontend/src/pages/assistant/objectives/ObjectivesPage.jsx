import { Link } from "react-router-dom";

export default function ObjectivesPage() {
  return (
    <div className="container my-5">
      <h1 className="mb-4">🎯 Assistant Objectives</h1>
      <p className="text-muted mb-4">
        Define goals for the assistant to pursue across tasks, milestones, and missions.
      </p>

      <Link to="/projects" className="btn btn-outline-secondary">
        🔙 Back to Projects
      </Link>
    </div>
  );
}