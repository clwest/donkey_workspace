import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import {
  fetchGlossaryMutations,
  acceptGlossaryMutation,
  rejectGlossaryMutation,
} from "../../api/agents";
import apiFetch from "../../utils/apiClient";

export default function GlossaryMutationReviewPanel() {
  const [mutations, setMutations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const load = async () => {
    try {
      const assistant = searchParams.get("assistant");
      const res = await fetchGlossaryMutations(
        assistant ? { assistant } : undefined
      );
      const data = res.results || res;
      if (!data || data.length === 0) {
        navigate("/anchor/symbolic", { replace: true });
      } else {
        setMutations(data);
      }
    } catch (err) {
      console.error("Failed to load mutations", err);
      navigate("/anchor/symbolic", { replace: true });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [searchParams]);

  const handleAccept = async (id) => {
    try {
      await acceptGlossaryMutation(id);
      setMutations(
        mutations.map((m) =>
          m.id === id ? { ...m, status: "applied" } : m
        )
      );
    } catch (err) {
      console.error("Failed to accept mutation", err);
      alert(err.message);
    }
  };

  const handleReject = async (id) => {
    await rejectGlossaryMutation(id);
    setMutations(mutations.map((m) => (m.id === id ? { ...m, status: "rejected" } : m)));
  };

  const handleEdit = async (id) => {
    const item = mutations.find((m) => m.id === id);
    const val = prompt("Update suggested term", item.suggested_label);
    if (!val) return;
    await apiFetch(`/memory/symbolic-anchors/${id}/`, {
      method: "PATCH",
      body: { suggested_label: val },
    });
    setMutations(mutations.map((m) => (m.id === id ? { ...m, suggested_label: val } : m)));
  };

  const total = mutations.length;
  const failing = mutations.filter((m) => m.fallback_count > 3).length;
  const applied = mutations.filter((m) => m.status === "applied").length;
  const convergence = total ? (((total - failing) / total) * 100).toFixed(0) : 0;

  if (loading) return <div className="container my-4">Loading...</div>;

  return (
    <div className="container my-4">
      <h1 className="mb-3">Glossary Mutations</h1>
      <div className="mb-3">
        <span className="badge bg-primary me-2">Total {total}</span>
        <span className="badge bg-warning text-dark me-2">Failing {failing}</span>
        <span className="badge bg-success me-2">Applied {applied}</span>
        <span className="badge bg-info text-dark">Convergence {convergence}%</span>
      </div>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Original Term</th>
            <th>Suggested Replacement</th>
            <th>Source</th>
            <th>Fallback Count</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {mutations.map((m) => (
            <tr key={m.id}>
              <td>{m.original_label}</td>
              <td>{m.suggested_label || "-"}</td>
              <td>{m.mutation_source}</td>
              <td>{m.fallback_count}</td>
              <td>{m.status}</td>
              <td>
                <button
                  className="btn btn-sm btn-success me-1"
                  disabled={m.status !== "pending" || !m.suggested_label}
                  onClick={() => handleAccept(m.id)}
                >
                  Accept
                </button>
                <button
                  className="btn btn-sm btn-danger me-1"
                  disabled={m.status !== "pending"}
                  onClick={() => handleReject(m.id)}
                >
                  Reject
                </button>
                <button className="btn btn-sm btn-secondary" onClick={() => handleEdit(m.id)}>
                  Edit
                </button>
              </td>
            </tr>
          ))}
          {mutations.length === 0 && (
            <tr>
              <td colSpan="6" className="text-muted">
                No mutations found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
