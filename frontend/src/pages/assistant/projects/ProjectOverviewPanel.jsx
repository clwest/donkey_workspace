import { Link } from "react-router-dom";

export default function ProjectOverviewPanel({ project, tasks, onCreateQuickTask, onPlanWithAI, onClearTasks }) {
  return (
    <div className="card p-3 shadow-sm">
      <h5 className="mb-3">📋 {project.title}</h5>
      <p className="text-muted small mb-3">
        Created: {new Date(project.created_at).toLocaleDateString()}
      </p>

      <p className="fw-bold">
        Tasks: {tasks.length}
      </p>

      <div className="d-grid gap-2 mb-3">
        <button onClick={onCreateQuickTask} className="btn btn-success btn-sm">
          ➕ Quick Add Task
        </button>
        <button onClick={onPlanWithAI} className="btn btn-primary btn-sm">
          🔥 Plan More (AI)
        </button>
        <Link to={`/assistants/projects/${project.id}/memories`} className="btn btn-outline-secondary btn-sm">
          🧠 View Linked Memories
        </Link>
      </div>

      <button onClick={onClearTasks} className="btn btn-outline-danger btn-sm w-100">
        🧹 Clear All Tasks
      </button>
    </div>
  );
}