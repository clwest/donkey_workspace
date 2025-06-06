import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Button, Alert } from "react-bootstrap";
import { toast } from "react-toastify";
import {
  fetchGlossaryMutations,
  rejectGlossaryMutation,
  acceptGlossaryMutation,
  suggestMissingGlossaryMutations,
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

  const reload = () => load();

  const handleAccept = async (id) => {
    try {
      await acceptGlossaryMutation(id);
      toast.success("Mutation accepted");
      reload();
    } catch (e) {
      toast.error("Failed to accept mutation");
    }
  };

  const handleReject = async (id) => {
    await rejectGlossaryMutation(id);
    reload();
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

  const runSuggestionJob = async () => {
    const assistant = searchParams.get("assistant");
    if (!assistant) return;
    try {
      await suggestMissingGlossaryMutations(assistant);
      toast.info("Suggestion job triggered");
      reload();
    } catch (e) {
      toast.error("Failed to run job");
    }
  };

  const showAll = import.meta.env.DEV || window.location.pathname.startsWith("/anchor/symbolic");
  const visible = showAll ? mutations : mutations.filter((m) => m.status === "pending");

  const total = visible.length;
  const failing = visible.filter((m) => m.fallback_count > 3).length;
  const applied = visible.filter((m) => m.status === "applied").length;
  const convergence = total ? (((total - failing) / total) * 100).toFixed(0) : 0;
  const missingSuggestions =
    visible.length > 0 && visible.every((m) => !m.suggested_label);

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
      {missingSuggestions && (
        <Alert variant="warning" className="mb-3">
          No suggestions available. Run <code>generate_missing_mutations</code> or
          click “Auto-Suggest Missing Labels.”
          <Button className="ms-2" size="sm" onClick={runSuggestionJob}>
            Auto-Suggest Missing Labels
          </Button>
        </Alert>
      )}
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
          {visible.map((m) => (
            <tr key={m.id}>
              <td>{m.original_label}</td>
              <td>{m.suggested_label || "-"}</td>
              <td>{m.mutation_source}</td>
              <td>{m.fallback_count}</td>
              <td>
                {m.status}
                {showAll && m.status === "applied" && (
                  <span className="badge bg-success ms-1">✅ Applied</span>
                )}
                {showAll && m.status === "rejected" && (
                  <span className="badge bg-danger ms-1">❌ Rejected</span>
                )}
              </td>
              <td>
                <Button
                  className="bg-green-600 hover:bg-green-700 me-1"
                  disabled={m.status !== "pending" || !m.suggested_label}
                  onClick={() => handleAccept(m.id)}
                >
                  Accept
                </Button>
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
          {visible.length === 0 && (
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
