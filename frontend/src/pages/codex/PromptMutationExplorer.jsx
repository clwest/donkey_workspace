import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function PromptMutationExplorer() {
  const [data, setData] = useState(null);

  useEffect(() => {
    apiFetch("/codex/evolve/")
      .then((res) => setData(res.results || res))
      .catch((err) => console.error("Failed to load mutations", err));
  }, []);

  return (
    <div className="container my-4">
      <h3>Codex Evolution</h3>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
