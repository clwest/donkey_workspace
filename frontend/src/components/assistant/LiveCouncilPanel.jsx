import { useEffect, useState } from "react";
import { fetchCouncilThoughts } from "../../api/council";

export default function LiveCouncilPanel({ sessionId }) {
  const [thoughts, setThoughts] = useState([]);

  useEffect(() => {
    if (!sessionId) return;
    async function load() {
      try {
        const res = await fetchCouncilThoughts(sessionId);
        setThoughts(res);
      } catch (err) {
        console.error("Failed to load council thoughts", err);
      }
    }
    load();
    const t = setInterval(load, 3000);
    return () => clearInterval(t);
  }, [sessionId]);

  return (
    <div className="mt-3">
      {thoughts.map((t) => (
        <div key={t.id} className="border rounded p-2 mb-2">
          <strong>{t.assistant_name}</strong>: {t.content}
        </div>
      ))}
    </div>
  );
}
