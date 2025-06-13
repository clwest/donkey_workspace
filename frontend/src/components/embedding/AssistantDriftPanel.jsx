import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { fetchDriftSummary, retryContextRepair } from "../../api/assistants";

export default function AssistantDriftPanel({ slug }) {
  const [rows, setRows] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const res = await fetchDriftSummary(slug);
      setRows(res);
    } catch {
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [slug]);

  const retry = async (contextId) => {
    await retryContextRepair(contextId);
    load();
  };

  if (loading) return <div>Loading drift data...</div>;
  if (!rows || rows.length === 0) return <div>No drift detected.</div>;

  return (
    <div className="mt-3">
      <h4>Embedding Drift</h4>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Context ID</th>
            <th>Mismatches</th>
            <th>Fixed</th>
            <th>% Failure</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.context_id}>
              <td>{r.context_id}</td>
              <td>{r.mismatched}</td>
              <td>{r.repaired}</td>
              <td>
                {r.repaired + r.failed
                  ? ((r.failed / (r.repaired + r.failed)) * 100).toFixed(1)
                  : "0"}
                %
              </td>
              <td>
                <button
                  className="btn btn-sm btn-outline-primary"
                  onClick={() => retry(r.context_id)}
                >
                  Retry Repair
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

AssistantDriftPanel.propTypes = {
  slug: PropTypes.string.isRequired,
};
