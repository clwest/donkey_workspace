import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

const MissionArchetypeBrowser = () => {
  const [archetypes, setArchetypes] = useState([]);
  const [form, setForm] = useState({ name: "", description: "" });

  useEffect(() => {
    apiFetch("/agents/archetypes/")
      .then(setArchetypes)
      .catch((err) => console.error("Failed to load archetypes", err));
  }, []);

  const handleCreate = async () => {
    try {
      const newArc = await apiFetch("/agents/archetypes/", {
        method: "POST",
        body: form,
      });
      setArchetypes([...archetypes, newArc]);
      setForm({ name: "", description: "" });
    } catch (err) {
      console.error("Create failed", err);
    }
  };

  return (
    <div>
      <h5>Mission Archetypes</h5>
      <ul className="list-group mb-3">
        {archetypes.map((a) => (
          <li key={a.id} className="list-group-item">
            <strong>{a.name}</strong>
            <div>{a.description}</div>
          </li>
        ))}
        {archetypes.length === 0 && (
          <li className="list-group-item text-muted">No archetypes.</li>
        )}
      </ul>
      <div className="mb-2">
        <input
          type="text"
          className="form-control mb-2"
          placeholder="Name"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
        <textarea
          className="form-control mb-2"
          placeholder="Description"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        ></textarea>
        <button className="btn btn-sm btn-primary" onClick={handleCreate}>
          Add Archetype
        </button>
      </div>
    </div>
  );
};

export default MissionArchetypeBrowser;

