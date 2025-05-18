import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import { toast } from "react-toastify";

export default function AssistantSpawnForm({ creatorId, projectId }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [specialty, setSpecialty] = useState("");
  const [promptId, setPromptId] = useState("");
  const [prompts, setPrompts] = useState([]);

  useEffect(() => {
    const loadPrompts = async () => {
      try {
        const res = await apiFetch("/prompts/?type=system");
        setPrompts(res);
      } catch (err) {
        toast.error("Failed to load prompts");
        console.error(err);
      }
    };
    loadPrompts();
  }, []);

  async function handleSpawn() {
    if (!name || !description || !specialty || !promptId) {
      toast.warning("Fill in all fields before spawning.");
      return;
    }

    try {
      const res = await apiFetch("/assistants/create_from_thought/", {
        method: "POST",
        body: {
          name,
          description,
          specialty,
          prompt_id: promptId,
          created_by: creatorId,
          project_id: projectId,
        },
      });

      toast.success(`🧙‍♂️ Zeno spawned ${res.name}!`);
      setName("");
      setDescription("");
      setSpecialty("");
      setPromptId("");
    } catch (err) {
      toast.error("❌ Failed to spawn assistant.");
      console.error(err);
    }
  }

  return (
    <div className="mt-5 border p-3 rounded bg-light">
      <h5>🪄 Spawn a New Assistant</h5>

      <input
        className="form-control mb-2"
        placeholder="Name (e.g. Cursor Jr)"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <input
        className="form-control mb-2"
        placeholder="Specialty (e.g. AI Code Reviews)"
        value={specialty}
        onChange={(e) => setSpecialty(e.target.value)}
      />
      <textarea
        className="form-control mb-2"
        placeholder="Description"
        rows={3}
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <select
        className="form-select mb-3"
        value={promptId}
        onChange={(e) => setPromptId(e.target.value)}
      >
        <option value="">Select system prompt...</option>
        {prompts.map((p) => (
          <option key={p.id} value={p.id}>
            {p.title}
          </option>
        ))}
      </select>

      <button className="btn btn-primary" onClick={handleSpawn}>
        🧬 Spawn Assistant
      </button>
    </div>
  );
}