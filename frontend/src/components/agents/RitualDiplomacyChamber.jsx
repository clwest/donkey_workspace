import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualDiplomacyChamber() {
  const [ritualType, setRitualType] = useState("");
  const [offering, setOffering] = useState("");
  const [stake, setStake] = useState("");
  const [message, setMessage] = useState("");

  const startRitual = async () => {
    try {
      await apiFetch("/agents/myth-diplomacy/", {
        method: "POST",
        body: {
          topic: stake,
          ritual_type: ritualType,
          symbolic_offering: offering,
        },
      });
      setMessage("Ceremony initiated.");
    } catch {
      setMessage("Failed to start diplomacy.");
    }
  };

  return (
    <div className="my-3">
      <h5>Ritual Diplomacy Chamber</h5>
      <input
        className="form-control mb-2"
        placeholder="Ritual Type"
        value={ritualType}
        onChange={(e) => setRitualType(e.target.value)}
      />
      <input
        className="form-control mb-2"
        placeholder="Symbolic Offering"
        value={offering}
        onChange={(e) => setOffering(e.target.value)}
      />
      <input
        className="form-control mb-2"
        placeholder="Myth Stake"
        value={stake}
        onChange={(e) => setStake(e.target.value)}
      />
      <button className="btn btn-primary" onClick={startRitual}>
        Begin Ritual
      </button>
      {message && <div className="mt-2">{message}</div>}
    </div>
  );
}
