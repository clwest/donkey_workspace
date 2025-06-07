import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "@/utils/apiClient";

export default function MemoryChainsListPage() {
  const [chains, setChains] = useState([]);

  useEffect(() => {
    async function fetchChains() {
      try {
        const data = await apiFetch("/v1/memory/chains/list/");
        setChains(data);
      } catch (err) {
        console.error("Error fetching memory chains:", err);
      }
    }
    fetchChains();
  }, []);

  if (chains.length === 0) return <div className="container my-5">No memory chains yet.</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-4">🧠 Memory Chains</h1>

      <div className="list-group mb-4">
        {chains.map((chain) => (
          <Link
            to={`/memories/chains/${chain.id}`}
            className="list-group-item list-group-item-action"
            key={chain.id}
          >
            <strong>{chain.title}</strong>
            <br />
            <small className="text-muted">
              Created: {new Date(chain.created_at).toLocaleDateString()}
            </small>
          </Link>
        ))}
      </div>

      <Link to="/memories" className="btn btn-secondary">
        ⬅️ Back to Memories
      </Link>
    </div>
  );
}