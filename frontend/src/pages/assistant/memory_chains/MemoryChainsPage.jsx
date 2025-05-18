import { Link } from "react-router-dom";

export default function MemoryChainsPage() {
  return (
    <div className="container my-5">
      <h1 className="mb-4">🧠 Memory Chains</h1>
      <p className="text-muted mb-4">
        Create and manage chains of memories to power advanced assistant reasoning.
      </p>

      <Link to="/assistants/projects" className="btn btn-outline-secondary">
        🔙 Back to Projects
      </Link>
    </div>
  );
}