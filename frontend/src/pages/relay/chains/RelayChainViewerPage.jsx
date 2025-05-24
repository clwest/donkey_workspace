import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import RelayChainViewer from "../../../components/relay/RelayChainViewer";

const mockChain = {
  id: "demo",
  nodes: [
    {
      id: "a",
      assistant: "Assistant A",
      message: "Initial message",
      status: "delivered",
      timestamp: new Date().toISOString(),
    },
    {
      id: "b",
      assistant: "Assistant B",
      message: "Forwarded message",
      status: "pending",
    },
  ],
};

export default function RelayChainViewerPage() {
  const { id } = useParams();
  const [chain, setChain] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch(`/relay/chains/${id}/`)
      .then(setChain)
      .catch(() => setChain(mockChain))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="container my-5">Loading chain...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-4">Relay Chain Viewer</h1>
      <RelayChainViewer chain={chain} />
    </div>
  );
}
