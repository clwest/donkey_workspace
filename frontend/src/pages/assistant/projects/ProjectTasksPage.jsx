import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export default function ProjectTasksPage() {
  const { id } = useParams();
  const [tasks, setTasks] = useState([]);
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(false);
  const [planning, setPlanning] = useState(false);
  const [editingTaskId, setEditingTaskId] = useState(null);
  const [editedTitle, setEditedTitle] = useState("");

  useEffect(() => {
    async function fetchProject() {
      const res = await fetch(`/api/assistants/projects/${id}/`);
      const data = await res.json();
      setProject(data);
    }
    async function fetchTasks() {
      const res = await fetch(`/api/assistants/projects/${id}/tasks/`);
      const data = await res.json();
      setTasks(data);
    }
    fetchProject();
    fetchTasks();
  }, [id]);

  async function handlePlan() {
    setPlanning(true);
    const res = await fetch(`/api/assistants/projects/${id}/ai_plan/`, {
      method: "POST",
    });
    const data = await res.json();
    setTasks(prev => [...prev, ...data]);
    setPlanning(false);
  }

  function startEditing(task) {
    setEditingTaskId(task.id);
    setEditedTitle(task.title);
  }

  function cancelEditing() {
    setEditingTaskId(null);
    setEditedTitle("");
  }

  async function saveTask(taskId) {
    await fetch(`/api/assistants/tasks/${taskId}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: editedTitle }),
    });
    setTasks(prev =>
      prev.map(t => (t.id === taskId ? { ...t, title: editedTitle } : t))
    );
    cancelEditing();
  }

  async function deleteTask(taskId) {
    if (!window.confirm("Are you sure you want to delete this task?")) return;

    await fetch(`/api/assistants/tasks/${taskId}/`, {
      method: "DELETE",
    });
    setTasks(prev => prev.filter(t => t.id !== taskId));
  }

  if (!project) return <div className="container my-5">Loading project...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-4">{project.title}</h1>
      <p className="text-muted">{project.description}</p>

      {/* Auto-task suggestion */}
      {!tasks.length && (
        <button onClick={handlePlan} disabled={planning} className="btn btn-primary my-3">
          {planning ? "Planning..." : "✨ Suggest Starter Tasks"}
        </button>
      )}

      {/* Task list */}
      <ul className="list-group mt-4">
        {tasks.map(task => (
          <li key={task.id} className="list-group-item d-flex justify-content-between align-items-center">
            {editingTaskId === task.id ? (
              <div className="d-flex flex-grow-1 gap-2">
                <input
                  type="text"
                  className="form-control"
                  value={editedTitle}
                  onChange={(e) => setEditedTitle(e.target.value)}
                />
                <button className="btn btn-success btn-sm" onClick={() => saveTask(task.id)}>💾 Save</button>
                <button className="btn btn-secondary btn-sm" onClick={cancelEditing}>✖️ Cancel</button>
              </div>
            ) : (
              <>
                <div className="flex-grow-1">
                  <span>{task.title}</span>
                  {task.tone && (
                    <span className="badge bg-secondary ms-2">{task.tone}</span>
                  )}
                  {task.generated_from_mood && (
                    <div className="text-muted small">from mood: {task.generated_from_mood}</div>
                  )}
                </div>
                <div className="btn-group">
                  <button className="btn btn-outline-primary btn-sm" onClick={() => startEditing(task)}>✏️</button>
                  <button className="btn btn-outline-danger btn-sm" onClick={() => deleteTask(task.id)}>🗑️</button>
                </div>
              </>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}