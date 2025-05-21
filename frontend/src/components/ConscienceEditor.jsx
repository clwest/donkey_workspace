import { useState, useEffect } from "react";
import apiFetch from "../utils/apiClient";

export default function ConscienceEditor({ assistantSlug }) {
  const [profile, setProfile] = useState(null);
  const [values, setValues] = useState("");
  const [constraints, setConstraints] = useState("");

  useEffect(() => {
    const load = async () => {
      if (!assistantSlug) return;
      const data = await apiFetch(`/assistants/?slug=${assistantSlug}`);
      if (data && data.length > 0) {
        const assistant = data[0];
        if (assistant.conscience) {
          setProfile(assistant.conscience);
          setValues(JSON.stringify(assistant.conscience.core_values || {}));
          setConstraints(
            JSON.stringify(assistant.conscience.ethical_constraints || {})
          );
        }
      }
    };
    load();
  }, [assistantSlug]);

  const save = async () => {
    await apiFetch(`/conscience/`, {
      method: "POST",
      body: {
        assistant: profile ? profile.assistant : assistantSlug,
        core_values: JSON.parse(values || "{}"),
        ethical_constraints: JSON.parse(constraints || "{}"),
      },
    });
  };

  if (!profile) return <div>No conscience defined.</div>;

  return (
    <div className="p-3 border rounded bg-light">
      <h5>Conscience Profile</h5>
      <textarea
        className="form-control mb-2"
        value={values}
        onChange={(e) => setValues(e.target.value)}
        rows={3}
      />
      <textarea
        className="form-control mb-2"
        value={constraints}
        onChange={(e) => setConstraints(e.target.value)}
        rows={3}
      />
      <button className="btn btn-sm btn-primary" onClick={save}>
        Save
      </button>
    </div>
  );
}
