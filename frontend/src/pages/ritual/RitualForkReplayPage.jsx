import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualForkReplayPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    apiFetch("/ritual/fork/replay/")
      .then(setData)
      .catch((err) => console.error("Failed to load replay", err));
  }, []);

  return (
    <div className="container my-4">
      <h3>Ritual Fork Replay</h3>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
