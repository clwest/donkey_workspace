import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SwarmTaskEvolutionPage() {
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    apiFetch("/evolve/swarm/")
      .then((res) => setSuggestions(res.results || res))
      .catch((err) => console.error("Failed to load suggestions", err));
  }, []);

  return (
    <div className="container my-4">
      <h3>Swarm Task Evolution</h3>
      <pre>{JSON.stringify(suggestions, null, 2)}</pre>
    </div>
  );
}
