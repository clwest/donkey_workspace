import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DivineTaskConsole() {
  const [tasks, setTasks] = useState([]);
  const [assistants, setAssistants] = useState([]);
  const [assigning, setAssigning] = useState({});

  useEffect(() => {
    async function load() {
      try {
        const t = await apiFetch("/swarm/divine-tasks/");
        setTasks(t.results || t);
        const a = await apiFetch("/assistants/?limit=100");
        setAssistants(a.results || a);
      } catch (err) {
        console.error("Failed to load divine tasks", err);
      }
    }
    load();
  }, []);

  const assignTask = async (taskId, assistantId) => {
    if (!assistantId) return;
    setAssigning((p) => ({ ...p, [taskId]: true }));
    try {
      await apiFetch(`/swarm/divine-tasks/${taskId}/assign/`, {
        method: "POST",
        body: { assistant: assistantId },
      });
      setTasks((prev) =>
        prev.map((t) =>
          t.id === taskId ? { ...t, assigned_to: assistantId } : t,
        ),
      );
    } catch (err) {
      console.error("Failed to assign task", err);
    } finally {
      setAssigning((p) => ({ ...p, [taskId]: false }));
    }
  };

  return (
    <div className="my-3">
      <h5>Divine Tasks</h5>
      <ul className="list-group">
        {tasks.map((t) => (
          <li key={t.id} className="list-group-item">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <strong>{t.name}</strong> — {t.deity_name || t.deity}
              </div>
              <div>
                <select
                  className="form-select form-select-sm"
                  value={t.assigned_to || ""}
                  onChange={(e) => assignTask(t.id, e.target.value)}
                  disabled={assigning[t.id]}
                >
                  <option value="">Assign...</option>
                  {assistants.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </li>
        ))}
        {tasks.length === 0 && (
          <li className="list-group-item text-muted">No active divine tasks.</li>
        )}
      </ul>
    </div>
  );
}
