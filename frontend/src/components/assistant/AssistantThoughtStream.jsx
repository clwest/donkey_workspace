import { useEffect, useState } from "react";

import apiFetch from "@/utils/apiClient";
import ThoughtLogCard from "@/components/assistant/thoughts/ThoughtLogCard";

export default function AssistantThoughtStream({ assistantId }) {
  const [thoughts, setThoughts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);


  useEffect(() => {
    if (!assistantId) return;
    setLoading(true);

    apiFetch(`/assistants/${assistantId}/thought-log/`, { params: { limit: 20 } })
      .then((res) => setThoughts(res.results || res))
      .catch((err) => {
        console.error("Failed to load thought stream", err);
        setError("Failed to load thoughts");
        setThoughts([]);
      })

      .finally(() => setLoading(false));
  }, [assistantId]);

  return (

    <div className="p-2 border rounded">
      <h5>Thought Stream</h5>
      {loading && <div>Loading thoughts...</div>}
      {error && <div className="text-red-500 text-sm">{error}</div>}
      {thoughts.length === 0 && !loading ? (
        <div className="text-muted">{error ? "Failed to load" : "Awaiting assistant thoughts"}</div>
      ) : (
        <div className="space-y-2">
          {thoughts.map((t) => (
            <ThoughtLogCard key={t.id} thought={t} />
          ))}
        </div>
      )}

    </div>
  );
}
