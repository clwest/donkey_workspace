import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchCascadeGraph } from "../../api/ontology";
import MythgraphGraph from "../../components/mythgraph/MythgraphGraph";

export default function CascadeGraphPage() {
  const { clauseId } = useParams();
  const [graph, setGraph] = useState(null);

  useEffect(() => {
    if (!clauseId) return;
    fetchCascadeGraph(clauseId)
      .then(setGraph)
      .catch(() => setGraph(null));
  }, [clauseId]);

  return (
    <div className="container my-4">
      <h1 className="mb-3">Codex Cascade</h1>
      {graph ? (
        <>
          <MythgraphGraph data={graph} />
          {graph.meta && (
            <div className="mt-2">
              <strong>Symbolic Drift:</strong> {graph.meta.symbolic_drift_score}
            </div>
          )}
        </>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}
