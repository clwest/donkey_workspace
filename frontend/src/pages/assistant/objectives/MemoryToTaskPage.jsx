// src/pages/assistant/tasks/MemoryToTaskPage.jsx
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

export default function MemoryToTaskPage() {
  const { memoryId } = useParams();
  const navigate = useNavigate();
  const [memory, setMemory] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [taskTitle, setTaskTitle] = useState("");

  useEffect(() => {
    async function fetchMemory() {
      const res = await fetch(`http://localhost:8000/api/memory/${memoryId}/`);
      const data = await res.json();
      setMemory(data);
    }
    async function fetchProjects() {
      const res = await fetch(`http://localhost:8000/api/assistants/projects/`);
      const data = await res.json();
      setProjects(data);
    }
    fetchMemory();
    fetchProjects();
  }, [memoryId]);

  async function handleCreateTask() {
    if (!selectedProjectId || !taskTitle) {
      alert("Please select a project and enter a task title.");
      return;
    }

    const res = await fetch(`http://localhost:8000/api/assistants/projects/${selectedProjectId}/tasks/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: taskTitle,
        description: memory?.event || "",
      }),
    });

    if (res.ok) {
      alert("✅ Task created from memory!");
      navigate(`/projects/${selectedProjectId}`);
    } else {
      alert("❌ Failed to create task.");
    }
  }

  if (!memory) return <div className="container my-5">Loading memory...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-4">🛠️ Turn Memory into Task</h1>

      <div className="mb-4">
        <h5>Memory:</h5>
        <p className="bg-light p-3 rounded">{memory.event}</p>
      </div>

      <div className="mb-4">
        <label className="form-label">Choose Project</label>
        <select
          className="form-select"
          value={selectedProjectId}
          onChange={(e) => setSelectedProjectId(e.target.value)}
        >
          <option value="">Select...</option>
          {projects.map((project) => (
            <option key={project.id} value={project.id}>
              {project.title}
            </option>
          ))}
        </select>
      </div>

      <div className="mb-4">
        <label className="form-label">Task Title</label>
        <input
          type="text"
          className="form-control"
          value={taskTitle}
          onChange={(e) => setTaskTitle(e.target.value)}
          placeholder="New task title..."
        />
      </div>

      <button
        className="btn btn-primary"
        onClick={handleCreateTask}
        disabled={!selectedProjectId || !taskTitle}
      >
        🚀 Create Task
      </button>
    </div>
  );
}