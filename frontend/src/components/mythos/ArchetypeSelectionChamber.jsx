import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

export default function ArchetypeSelectionChamber() {
  const [tone, setTone] = useState("");
  const [tag, setTag] = useState("");
  const navigate = useNavigate();

  const [searchParams] = useSearchParams();
  const path = searchParams.get("path") || "custom";


  const submit = () => {
    navigate("/onboarding/summon", { state: { tone, tag, path } });
  };

  return (
    <div className="container my-4">
      <h2>Archetype Selection</h2>
      <div className="mb-2">
        <label className="form-label">Preferred Tone</label>
        <input
          className="form-control"
          value={tone}
          onChange={(e) => setTone(e.target.value)}
        />
      </div>
      <div className="mb-2">
        <label className="form-label">Symbolic Tag</label>
        <input
          className="form-control"
          value={tag}
          onChange={(e) => setTag(e.target.value)}
        />
      </div>
      <button className="btn btn-primary" onClick={submit} disabled={!tone || !tag}>
        Continue
      </button>
    </div>
  );
}
