import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualNetworkDashboard() {
  const [ritual, setRitual] = useState(null);
  const [loading, setLoading] = useState(false);

  async function generate() {
    setLoading(true);
    try {
      const res = await apiFetch("/ritual-network/", { method: "POST" });
      setRitual(res);
    } catch (err) {
      console.error("Failed to generate ritual", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="my-3">
      <h5>Ritual Network</h5>
      <button className="btn btn-sm btn-primary mb-2" onClick={generate} disabled={loading}>
        {loading ? "Generating..." : "Generate Ritual"}
      </button>
      {ritual && (
        <pre className="bg-light p-2 border">
          {JSON.stringify(ritual, null, 2)}
        </pre>
      )}
    </div>
  );
}
