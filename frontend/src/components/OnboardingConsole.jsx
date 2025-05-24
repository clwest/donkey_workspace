import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import apiFetch from "../utils/apiClient";

export default function OnboardingConsole() {
  const [name, setName] = useState("");
  const [archetype, setArchetype] = useState("");
  const [created, setCreated] = useState(null);
  const [params] = useSearchParams();
  const path = params.get("path") || "";

  const submit = async () => {
    const body = {
      assistant: { name, specialty: "" },
      identity_card: { archetype, symbolic_tags: [], myth_path: path, purpose_signature: "" },
      path,
    };
    const res = await apiFetch("/onboarding/", { method: "POST", body });
    setCreated(res.identity_card);
  };

  return (
    <div className="card my-3">
      <div className="card-header">Onboarding Console</div>
      <div className="card-body">
        <div className="mb-2">
          <label className="form-label">Name</label>
          <input className="form-control" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div className="mb-2">
          <label className="form-label">Archetype</label>
          <input className="form-control" value={archetype} onChange={(e) => setArchetype(e.target.value)} />
        </div>
        <button className="btn btn-primary" onClick={submit} disabled={!name || !archetype}>
          Create
        </button>
        {created && (
          <div className="mt-3 alert alert-success">Created card {created.id}</div>
        )}
      </div>
    </div>
  );
}
