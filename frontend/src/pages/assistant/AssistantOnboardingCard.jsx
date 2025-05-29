import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { onboardAssistant } from "../../api/assistants";

export default function AssistantOnboardingCard() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [archetype, setArchetype] = useState("");
  const [symbol, setSymbol] = useState("");
  const [reflection, setReflection] = useState("");

  const save = async () => {
    await onboardAssistant(id, {
      archetype,
      dream_symbol: symbol,
      init_reflection: reflection,
    });
    navigate(`/assistants/${id}/dream/console`);
  };

  return (
    <div className="container my-5">
      <h1>Assistant Identity Card</h1>
      <div className="mb-2">
        <label className="form-label">Archetype</label>
        <input
          className="form-control"
          value={archetype}
          onChange={(e) => setArchetype(e.target.value)}
        />
      </div>
      <div className="mb-2">
        <label className="form-label">Dream Symbol</label>
        <input
          className="form-control"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
        />
      </div>
      <div className="mb-2">
        <label className="form-label">Initial Reflection</label>
        <textarea
          className="form-control"
          value={reflection}
          onChange={(e) => setReflection(e.target.value)}
        />
      </div>
      <button className="btn btn-primary" onClick={save}>
        Save
      </button>
    </div>
  );
}
