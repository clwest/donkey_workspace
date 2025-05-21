import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function TimelineForkViewer({ rootId }) {
  const [branches, setBranches] = useState([]);

  useEffect(() => {
    if (!rootId) return;
    apiFetch(`/memory/branches/`, { params: { root_entry: rootId } })
      .then(setBranches)
      .catch(() => {});
  }, [rootId]);

  async function approve(id, value) {
    await apiFetch(`/memory/branches/${id}/`, {
      method: "PATCH",
      body: { approved: value },
    });
    const data = await apiFetch(`/memory/branches/`, { params: { root_entry: rootId } });
    setBranches(data);
  }

  if (branches.length === 0) return <div>No timeline forks.</div>;

  return (
    <div className="mt-3">
      <h5>Timeline Forks</h5>
      <ul className="list-group">
        {branches.map((b) => (
          <li key={b.id} className="list-group-item">
            <div className="fw-semibold">{b.fork_reason}</div>
            <div className="mb-2 text-muted" style={{ whiteSpace: "pre-wrap" }}>{b.speculative_outcome}</div>
            <div>
              <button
                className="btn btn-sm btn-outline-success me-2"
                onClick={() => approve(b.id, true)}
              >
                Approve
              </button>
              <button
                className="btn btn-sm btn-outline-danger"
                onClick={() => approve(b.id, false)}
              >
                Deny
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
