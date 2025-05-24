import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ExecutionChainPlanner() {
  const [chains, setChains] = useState([]);

  useEffect(() => {
    apiFetch("/plan/chains/")
      .then((res) => setChains(res.results || res))
      .catch(() => setChains([]));
  }, []);

  if (!chains) return <div>Loading chains...</div>;

  return <pre>{JSON.stringify(chains, null, 2)}</pre>;
}
