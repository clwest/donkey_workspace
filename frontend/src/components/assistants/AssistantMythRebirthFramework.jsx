import { useState } from "react";
import apiFetch from "../../utils/apiClient"

export default function AssistantMythRebirthFramework({ assistantId }) {
  const [name, setName] = useState("");
  const submit = () => {
    apiFetch(`/agents/assistants/${assistantId}/rebirth/`, {
      method: "POST",
      body: { name },
    }).then(() => alert("Rebirth initiated"));
  };
  return (
    <div className="p-2 border rounded">
      <h5>Assistant Rebirth</h5>
      <input
        className="form-control mb-2"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="New name"
      />
      <button className="btn btn-primary" onClick={submit} disabled={!name}>
        Rebirth
      </button>
    </div>
  );
}
