import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "@/utils/apiClient";

export default function ProjectTaskEditorPage() {
  const { id } = useParams();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newTaskContent, setNewTaskContent] = useState("");

  useEffect(() => {
    async function fetchTasks() {
      const data = await apiFetch(`/assistants/projects/${id}/tasks/`);
      setTasks(data);
    }
    fetchTasks();
  }, [id]);

  async function handleDelete(taskId) {
    await apiFetch(`/assistants/projects/tasks/${taskId}/`, {
      method: "DELETE",
    });
    setTasks(prev => prev.filter(task => task.id !== taskId));
  }

  async function handleSave(taskId, newContent) {
    const res = await apiFetch(`/assistants/projects/tasks/${taskId}/`, {
      method: "PATCH",
      body: { title: newContent },
    });

    if (res.ok) {
      setTasks(prev =>
        prev.map(task =>
          task.id === taskId ? { ...task, title: newContent } : task
        )
      );
    }
  }

  async function handleAddNewTask() {
    if (!newTaskContent.trim()) return;

    const res = await apiFetch(`/assistants/projects/${id}/tasks/`, {
      method: "POST",
      body: { title: newTaskContent },
    });

    if (res.ok) {
      const data = await res.json();
      setTasks(prev => [...prev, data]);
      setNewTaskContent("");
    }
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">📝 Edit Project Tasks</h1>

      <div className="mb-5">
        {tasks.map(task => (
          <TaskEditorRow
            key={task.id}
            task={task}
            onSave={handleSave}
            onDelete={handleDelete}
          />
        ))}
      </div>

      <div className="my-4">
        <input
          className="form-control mb-2"
          placeholder="New task title"
          value={newTaskContent}
          onChange={(e) => setNewTaskContent(e.target.value)}
        />
        <button onClick={handleAddNewTask} className="btn btn-success">
          ➕ Add Task
        </button>
      </div>

      <Link to={`/assistants/projects/${id}`} className="btn btn-outline-secondary mt-4">
        🔙 Back to Project
      </Link>
    </div>
  );
}

function TaskEditorRow({ task, onSave, onDelete }) {
  const [editContent, setEditContent] = useState(task.title);

  return (
    <div className="d-flex align-items-center gap-2 mb-3">
      <input
        className="form-control"
        value={editContent}
        onChange={(e) => setEditContent(e.target.value)}
      />
      <button className="btn btn-primary" onClick={() => onSave(task.id, editContent)}>
        💾 Save
      </button>
      <button className="btn btn-danger" onClick={() => onDelete(task.id)}>
        🗑️ Delete
      </button>
    </div>
  );
}