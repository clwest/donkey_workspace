import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Tabs, Tab } from "react-bootstrap";
import apiFetch from "../../../utils/apiClient";
import ChainSummaryPanel from "../../../components/memory/ChainSummaryPanel";
import MemoryFlowVisualizer from "../../../components/memory/MemoryFlowVisualizer";
import CrossThreadRecallPanel from "../../../components/memory/CrossThreadRecallPanel";
import EntropyTagPanel from "../../../components/memory/EntropyTagPanel";

export default function MemoryChainViewerPage() {
  const { id } = useParams();
  const [chain, setChain] = useState(null);
  const [summary, setSummary] = useState("");
  const [flowmap, setFlowmap] = useState(null);
  const [recallEntries, setRecallEntries] = useState(null);
  const [entropyTags, setEntropyTags] = useState([]);

  useEffect(() => {
    apiFetch(`/memory/chains/${id}/`).then(setChain).catch(() => {});
  }, [id]);

  useEffect(() => {
    if (!chain) return;
    apiFetch(`/memory/chains/${id}/flowmap/`).then(setFlowmap).catch(() => {});
    const tags = (chain.context_tags || []).filter((t) =>
      ["overlap", "decay", "loop"].some((k) => t.includes(k))
    );
    setEntropyTags(tags);
  }, [chain, id]);

  const handleSummarize = async () => {
    try {
      const data = await apiFetch(`/memory/chains/${id}/summarize/`);
      setSummary(data.summary);
    } catch (err) {
      console.error("Summary error", err);
    }
  };

  const handleRecall = async () => {
    try {
      const data = await apiFetch(`/memory/chains/${id}/cross_project_recall/`);
      setRecallEntries(data);
    } catch (err) {
      console.error("Recall error", err);
    }
  };

  if (!chain) return <div className="container my-5">Loading chain...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-3">🔗 {chain.title}</h1>
      <button className="btn btn-primary mb-3" onClick={handleSummarize}>
        🧠 Summarize Chain
      </button>
      <button className="btn btn-outline-primary mb-3 ms-2" onClick={handleRecall}>
        🔎 Recall from Linked Chains
      </button>
      {summary && <ChainSummaryPanel summary={summary} />}
      <EntropyTagPanel tags={entropyTags} />
      {recallEntries && <CrossThreadRecallPanel entries={recallEntries} />}

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