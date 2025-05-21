import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Tabs, Tab } from "react-bootstrap";
import apiFetch from "../../../utils/apiClient";
import ChainSummaryPanel from "../../../components/memory/ChainSummaryPanel";
import MemoryFlowVisualizer from "../../../components/memory/MemoryFlowVisualizer";

export default function MemoryChainViewerPage() {
  const { id } = useParams();
  const [chain, setChain] = useState(null);
  const [summary, setSummary] = useState("");
  const [flowmap, setFlowmap] = useState(null);

  useEffect(() => {
    apiFetch(`/memory/chains/${id}/`).then(setChain).catch(() => {});
  }, [id]);

  useEffect(() => {
    if (!chain) return;
    apiFetch(`/memory/chains/${id}/flowmap/`).then(setFlowmap).catch(() => {});
  }, [chain, id]);

  const handleSummarize = async () => {
    try {
      const data = await apiFetch(`/memory/chains/${id}/summarize/`);
      setSummary(data.summary);
    } catch (err) {
      console.error("Summary error", err);
    }
  };

  if (!chain) return <div className="container my-5">Loading chain...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-3">🔗 {chain.title}</h1>
      <button className="btn btn-primary mb-3" onClick={handleSummarize}>
        🧠 Summarize Chain
      </button>
      {summary && <ChainSummaryPanel summary={summary} />}

      <Tabs defaultActiveKey="memories" className="mt-3">
        <Tab eventKey="memories" title="Memories">
          <div className="list-group mb-4 mt-3">
            {chain.memories.map((memory) => (
              <div key={memory.id} className="list-group-item">
                <strong>
                  {new Date(chain.created_at).toLocaleDateString()}:
                </strong>
                <p>{memory.event}</p>
                {memory.emotion && (
                  <span className="badge bg-info text-dark">{memory.emotion}</span>
                )}
              </div>
            ))}
          </div>
        </Tab>
        <Tab eventKey="flow" title="🕸️ Visual Flowmap">
          <div className="mt-3">
            {flowmap ? (
              <MemoryFlowVisualizer data={flowmap} />
            ) : (
              <div>Loading flow...</div>
            )}
          </div>
        </Tab>
      </Tabs>

      <Link to="/memories" className="btn btn-secondary mt-3">
        ⬅️ Back to Memories
      </Link>
    </div>
  );
}