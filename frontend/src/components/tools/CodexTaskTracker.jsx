import React, { useState } from "react";

export default function CodexTaskTracker() {
  const [tasks, setTasks] = useState([
    {
      title: "Fix document reflection linkage (DevDoc → Document)",
      status: "in_progress",
    },
    {
      title: "Ensure Celery tasks run after documents are seeded",
      status: "todo",
    },
    {
      title: "Enable document reflection UI from /dev-dashboard",
      status: "todo",
    },
    {
      title: "Support DevDoc embedding and reflection retries",
      status: "todo",
    },
    {
      title: "Fix broken links in assistant reflections UI",
      status: "todo",
    },
  ]);

  const toggleStatus = (index) => {
    setTasks((prev) =>
      prev.map((task, i) => {
        if (i !== index) return task;
        const nextStatus =
          task.status === "todo"
            ? "in_progress"
            : task.status === "in_progress"
            ? "done"
            : "todo";
        return { ...task, status: nextStatus };
      })
    );
  };

  return (
    <div className="p-4 rounded bg-white border shadow-sm">
      <h3 className="text-xl font-bold mb-3">🧠 Codex Task Tracker</h3>
      <ul className="space-y-2">
        {tasks.map((task, idx) => (
          <li
            key={idx}
            className={`flex justify-between items-center px-3 py-2 rounded border cursor-pointer ${
              task.status === "done"
                ? "bg-green-100 border-green-300"
                : task.status === "in_progress"
                ? "bg-yellow-100 border-yellow-300"
                : "bg-gray-100 border-gray-300"
            }`}
            onClick={() => toggleStatus(idx)}
          >
            <span>{task.title}</span>
            <span className="text-xs uppercase font-bold">
              {task.status === "todo"
                ? "🕓 Todo"
                : task.status === "in_progress"
                ? "🚧 In Progress"
                : "✅ Done"}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}