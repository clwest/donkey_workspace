import { Link } from "react-router-dom";

export default function NextActionsPage() {
  return (
    <div className="container my-5">
      <h1 className="mb-4">📋 Next Actions</h1>
      <p className="text-muted mb-4">
        View prioritized next actions based on current objectives and project plans.
      </p>

      <Link to="/projects" className="btn btn-outline-secondary">
        🔙 Back to Projects
      </Link>
    </div>
  );
}