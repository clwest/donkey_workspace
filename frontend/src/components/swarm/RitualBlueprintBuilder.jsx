import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualBlueprintBuilder() {
  const [blueprints, setBlueprints] = useState([]);
  const [name, setName] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/ritual-blueprints/");
        setBlueprints(res.results || res);
      } catch (err) {
        console.error("Failed to load blueprints", err);
      }
    }
    load();
  }, []);

  const createBlueprint = async () => {
    if (!name) return;
    try {
      const bp = await apiFetch("/agents/ritual-blueprints/", {
        method: "POST",
        body: {
          name,
          creator: 1,
          symbolic_steps: {},
          transformation_goal: "goal",
          applicable_roles: [],
        },
      });
      setBlueprints((b) => [...b, bp]);
      setName("");
    } catch (err) {
      console.error("Failed to create blueprint", err);
    }
  };

  return (
    <div className="my-3">
      <h5>Ritual Blueprints</h5>
      <div className="mb-2">
        <input
          className="form-control"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Blueprint name"
        />
        <button className="btn btn-sm btn-primary mt-2" onClick={createBlueprint}>
          Add Blueprint
        </button>
      </div>
      <ul className="list-group">
        {blueprints.map((b) => (
          <li key={b.id} className="list-group-item">
            {b.name}
          </li>
        ))}
        {blueprints.length === 0 && (
          <li className="list-group-item text-muted">No blueprints.</li>
        )}
      </ul>
    </div>
  );
}
