import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export default function ProjectTaskManagerPage() {
  const { id: projectId } = useParams();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [roles, setRoles] = useState([]);
  const [filterAssistant, setFilterAssistant] = useState("");

  useEffect(() => {
    async function fetchTasks() {
      try {
        let url = `/assistants/projects/${projectId}/assistant-tasks/`;
        if (filterAssistant) url += `?assistant_id=${filterAssistant}`;
        const res = await fetch(`/api${url}`);
        if (!res.ok) throw new Error("Task fetch failed");
        const data = await res.json();
        setTasks(data);
      } catch (error) {
        console.error("Failed to fetch tasks:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchTasks();
    fetch(`/api/assistants/projects/${projectId}/roles/`)
      .then((r) => r.json())
      .then(setRoles);
  }, [projectId, filterAssistant]);

  async function handleStatusChange(taskId, newStatus) {
    try {
      await fetch(`/api/assistants/tasks/${taskId}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });

      setTasks(prevTasks =>
        prevTasks.map(task =>
          task.id === taskId ? { ...task, status: newStatus } : task
        )
      );
    } catch (error) {
      console.error("Failed to update task status:", error);
    }
  }

  if (loading) return <div>Loading tasks...</div>;

  return (
    <div className="mb-5">
      <h4 className="mb-3">🛠️ Tasks</h4>
      <div className="mb-2">
        <select
          className="form-select w-auto"
          value={filterAssistant}
          onChange={(e) => setFilterAssistant(e.target.value)}
        >
          <option value="">All assistants</option>
          {roles.map((r) => (
            <option key={r.id} value={r.assistant}>
              {r.assistant_name}
            </option>
          ))}
        </select>
      </div>

      {tasks.length === 0 ? (
        <p className="text-muted">No tasks yet.</p>
      ) : (
        <ul className="list-group">
          {tasks.map(task => (
            <li
              key={task.id}
              className="list-group-item py-2 px-3 d-flex justify-content-between align-items-center"
              style={{ fontSize: "0.9rem" }}
            >
              <div className="flex-grow-1 me-3">
                <strong>{task.title}</strong>
                {task.content && (
                  <div className="text-muted small">{task.content.slice(0, 80)}...</div>
                )}
              </div>
              <select
                className="form-select form-select-sm w-auto"
                value={task.status}
                onChange={(e) => handleStatusChange(task.id, e.target.value)}
              >
                <option value="todo">📝 To Do</option>
                <option value="in_progress">🚧 In Progress</option>
                <option value="done">✅ Done</option>
              </select>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}