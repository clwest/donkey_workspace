import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";
import AnchorConvergencePanel from "./AnchorConvergencePanel";

export default function AssistantGlossaryTrainingPanel({ assistantSlug }) {
  const [anchors, setAnchors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!assistantSlug) return;
    async function load() {
      try {
        const data = await apiFetch("/memory/symbolic-anchors/");
        const all = data.results || data;
        setAnchors(all.filter((a) => a.reinforced_by?.includes(assistantSlug)));
      } catch (err) {
        console.error("Failed to fetch anchors", err);
        setAnchors([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [assistantSlug]);

  if (loading) return <div>Loading glossary training...</div>;

  return (
    <div>
      {anchors.length === 0 ? (
        <div className="text-muted">No glossary convergence yet.</div>
      ) : (
        anchors.map((a) => (
          <div key={a.slug} className="mb-3">
            <h6>{a.label}</h6>
            <AnchorConvergencePanel anchorSlug={a.slug} />
          </div>
        ))
      )}
    </div>
  );
}
