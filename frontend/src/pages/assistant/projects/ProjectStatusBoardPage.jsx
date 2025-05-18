// src/pages/assistant/projects/ProjectStatusBoardPage.jsx
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

export default function ProjectStatusBoardPage() {
  const { id } = useParams(); // project ID
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    async function fetchTasks() {
      const res = await fetch(`http://localhost:8000/api/assistants/projects/${id}/tasks/`);
      const data = await res.json();
      setTasks(data);
    }
    fetchTasks();
  }, [id]);

  async function updateTaskStatus(taskId, newStatus) {
    await fetch(`http://localhost:8000/api/assistants/tasks/${taskId}/update_status/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });

    setTasks(prev => 
      prev.map(task => 
        task.id === taskId ? { ...task, status: newStatus } : task
      )
    );
  }

  function renderTasks(status) {
    return tasks
      .filter(task => task.status === status)
      .map(task => (
        <div key={task.id} className="card mb-3 shadow-sm">
          <div className="card-body">
            <h5 className="card-title">{task.title}</h5>
            <p className="card-text small text-muted">{task.description?.slice(0, 100)}</p>
            <div className="d-flex gap-2 mt-3">
              {status !== "completed" && (
                <button
                  className="btn btn-success btn-sm"
                  onClick={() => updateTaskStatus(task.id, "completed")}
                >
                  ✅ Mark Done
                </button>
              )}
              {status !== "in_progress" && (
                <button
                  className="btn btn-warning btn-sm"
                  onClick={() => updateTaskStatus(task.id, "in_progress")}
                >
                  🛠️ In Progress
                </button>
              )}
              {status !== "new" && (
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => updateTaskStatus(task.id, "new")}
                >
                  🆕 Reset
                </button>
              )}
            </div>
          </div>
        </div>
      ));
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">📋 Project Tasks Status Board</h1>

      <div className="row">
        <div className="col-md-4">
          <h4 className="text-center">🆕 New</h4>
          {renderTasks("new")}
        </div>

        <div className="col-md-4">
          <h4 className="text-center">🛠️ In Progress</h4>
          {renderTasks("in_progress")}
        </div>

        <div className="col-md-4">
          <h4 className="text-center">✅ Completed</h4>
          {renderTasks("completed")}
        </div>
      </div>

      <div className="text-center mt-5">
        <Link to="/assistants/projects" className="btn btn-outline-secondary">
          🔙 Back to Projects
        </Link>
      </div>
    </div>
  );
}