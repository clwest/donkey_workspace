import { useEffect, useState } from "react";
import { Button, Tabs, Tab } from "react-bootstrap";
import apiFetch from "../../utils/apiClient";
import { acceptGlossaryMutation, rejectGlossaryMutation } from "../../api/agents";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function SymbolicAnchorReviewPage() {
  useAuthGuard();
  const [anchors, setAnchors] = useState([]);
  const [tab, setTab] = useState("pending");
  const [editing, setEditing] = useState({});

  const load = async (status) => {
    const res = await apiFetch(`/memory/symbolic-anchors/`, {
      params: { mutation_status: status },
    });
    setAnchors(res.results || res);
  };

  useEffect(() => {
    load(tab);
  }, [tab]);

  const handleSave = async (id) => {
    const val = editing[id];
    await apiFetch(`/memory/symbolic-anchors/${id}/`, {
      method: "PATCH",
      body: { suggested_label: val },
    });
    load(tab);
  };

  const handleReject = async (id) => {
    await rejectGlossaryMutation(id);
    load(tab);
  };

  const approveAll = async () => {
    await Promise.all(
      anchors.map((a) => acceptGlossaryMutation(a.id))
    );
    load(tab);
  };

  const rejectAll = async () => {
    await Promise.all(anchors.map((a) => rejectGlossaryMutation(a.id)));
    load(tab);
  };

  const exportJson = () => {
    const data = JSON.stringify(anchors, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "anchors.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  const statusChip = (s) => {
    const map = {
      pending: "secondary",
      applied: "success",
      rejected: "danger",
    };
    return <span className={`badge bg-${map[s]}`}>{s}</span>;
  };

  return (
    <div className="container my-4">
      <h2 className="mb-3">Symbolic Anchor Review</h2>
      <Tabs activeKey={tab} onSelect={(k) => setTab(k)} className="mb-3">
        <Tab eventKey="pending" title="🕐 Pending Mutations" />
        <Tab eventKey="applied" title="✅ Approved" />
        <Tab eventKey="rejected" title="🛠️ Rejected" />
      </Tabs>
      <div className="mb-2 d-flex gap-2">
        {tab === "pending" && (
          <>
            <Button size="sm" onClick={approveAll}>
              Approve All ✓
            </Button>
            <Button size="sm" variant="danger" onClick={rejectAll}>
              Reject All ✗
            </Button>
          </>
        )}
        <Button size="sm" variant="outline-secondary" onClick={exportJson}>
          Export as JSON
        </Button>
      </div>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Label</th>
            <th>Suggested</th>
            <th>Source</th>
            <th>Score</th>
            <th>Assistant</th>
            <th>Context</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {anchors.map((a) => (
            <tr key={a.id}>
              <td>{a.label}</td>
              <td>
                <input
                  className="form-control form-control-sm"
                  value={editing[a.id] ?? a.suggested_label ?? ""}
                  onChange={(e) =>
                    setEditing({ ...editing, [a.id]: e.target.value })
                  }
                />
              </td>
              <td>{a.mutation_source || "-"}</td>
              <td>{a.fallback_score ?? "-"}</td>
              <td>{a.assistant || "-"}</td>
              <td>{a.memory_context || "-"}</td>
              <td>{statusChip(a.mutation_status)}</td>
              <td>
                {tab === "pending" && (
                  <>
                    <Button
                      size="sm"
                      className="me-1"
                      onClick={() => acceptGlossaryMutation(a.id).then(() => load(tab))}
                    >
                      ✓
                    </Button>
                    <Button
                      size="sm"
                      variant="danger"
                      className="me-1"
                      onClick={() => handleReject(a.id)}
                    >
                      ✗
                    </Button>
                    <Button size="sm" onClick={() => handleSave(a.id)}>
                      Save
                    </Button>
                  </>
                )}
                {tab !== "pending" && <span>-</span>}
              </td>
            </tr>
          ))}
          {anchors.length === 0 && (
            <tr>
              <td colSpan="8" className="text-muted">
                No anchors
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
