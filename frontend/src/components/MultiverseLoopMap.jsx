import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function MultiverseLoopMap() {
  const [loops, setLoops] = useState([]);
  useEffect(() => {
    apiFetch("/multiverse-loops/").then(setLoops);
  }, []);
  return (
    <div className="p-2 border rounded">
      <h5>Multiverse Loops</h5>
      <ul>
        {loops.map((l) => (
          <li key={l.id}>{l.anchor_assistant} - {l.loop_reason}</li>
        ))}
      </ul>
    </div>
  );
}
