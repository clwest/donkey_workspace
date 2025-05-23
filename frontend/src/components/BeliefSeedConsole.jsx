import { useState } from "react";
import apiFetch from "../utils/apiClient";

export default function BeliefSeedConsole({ assistantId }) {
  const [symbols, setSymbols] = useState("{}");
  const handleSend = () => {
    apiFetch("/belief-seeds/", {
      method: "POST",
      body: JSON.stringify({
        originating_entity: assistantId,
        core_symbol_set: JSON.parse(symbols || "{}"),
        intended_recipients: [assistantId],
        propagation_log: "seeded",
      }),
    }).then(() => alert("Seed sent"));
  };
  return (
    <div className="p-2 border rounded">
      <h5>Belief Seed</h5>
      <textarea
        className="form-control mb-2"
        value={symbols}
        onChange={(e) => setSymbols(e.target.value)}
        placeholder="{{}}"
      />
      <button className="btn btn-primary" onClick={handleSend}>
        Send Seed
      </button>
    </div>
  );
}
