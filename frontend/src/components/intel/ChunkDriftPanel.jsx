import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";
import { boostGlossaryAnchor } from "../../api/agents";

export default function ChunkDriftPanel() {
  const [data, setData] = useState(null);

  useEffect(() => {
    apiFetch("/intel/chunk_drift_stats/")
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data) return <div>Loading drift data...</div>;

  const handleBoost = async (slug) => {
    const val = window.prompt("Boost score", "0.2");
    if (!val) return;
    try {
      await boostGlossaryAnchor(slug, parseFloat(val));
      toast.success("Boost applied");
    } catch (err) {
      console.error(err);
      toast.error("Boost failed");
    }
  };

  const entries = Object.entries(data.drift_counts || {});
  const zeros = data.zero_match_anchors || [];

  return (
    <div className="p-2 border rounded">
      <h5>Chunk Drift</h5>
      {entries.length === 0 && zeros.length === 0 ? (
        <div className="text-muted">No drifting anchors</div>
      ) : (
        <>
          {entries.length > 0 && (
            <ul className="small mb-2">
              {entries.map(([slug, count]) => (
                <li key={slug}>
                  <strong>{slug}</strong> – {count} drifting chunks
                  <button
                    className="btn btn-sm btn-link ms-1"
                    onClick={() => handleBoost(slug)}
                  >
                    Boost
                  </button>
                </li>
              ))}
            </ul>
          )}
          {zeros.length > 0 && (
            <>
              <div className="h6">Zero Match Anchors</div>
              <ul className="small">
                {zeros.map((slug) => (
                  <li key={slug}>
                    {slug}
                    <button
                      className="btn btn-sm btn-link ms-1"
                      onClick={() => handleBoost(slug)}
                    >
                      Boost
                    </button>
                  </li>
                ))}
              </ul>
            </>
          )}
        </>
      )}
    </div>
  );
}
