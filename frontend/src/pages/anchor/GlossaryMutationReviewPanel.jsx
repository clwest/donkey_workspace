import { useEffect, useState } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { Button, Alert } from "react-bootstrap";
import AutoSuggestButton from "../../components/mutations/AutoSuggestButton";
import { toast } from "react-toastify";
import {
  fetchGlossaryMutations,
  rejectGlossaryMutation,
  acceptGlossaryMutation,
  testGlossaryMutations,
} from "../../api/agents";
import apiFetch from "../../utils/apiClient";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function GlossaryMutationReviewPanel() {
  useAuthGuard();
  const [mutations, setMutations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const load = async () => {
    try {
      const assistant = searchParams.get("assistant");
      const showAll =
        import.meta.env.DEV || window.location.pathname.startsWith("/anchor/symbolic");
      const params = assistant ? { assistant } : {};
      if (showAll) params.include = "all";
      const res = await fetchGlossaryMutations(params);
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
    async function checkAdmin() {
      try {
        const user = await apiFetch("/auth/user/", { allowUnauthenticated: true });
        setIsAdmin(user.is_staff || user.is_superuser);
      } catch {
        setIsAdmin(false);
      }
    }
    checkAdmin();
  }, [searchParams]);

  const reload = () => load();

  const handleAccept = async (id) => {
    try {
      await acceptGlossaryMutation(id);
      toast.success("Mutation accepted");
      setMutations((m) => m.filter((x) => x.id !== id));
    } catch (e) {
      toast.error("Failed to accept mutation");
    }
  };

  const handleReject = async (id) => {
    await rejectGlossaryMutation(id);
    setMutations((m) => m.filter((x) => x.id !== id));
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


  const runTestJob = async () => {
    const assistant = searchParams.get("assistant");
    if (!assistant) return;
    try {
      await testGlossaryMutations(assistant);
      toast.info("Mutation test started");
      reload();
    } catch (e) {
      toast.error("Failed to run tests");
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
        <Link to="/keeper/logs" className="btn btn-sm btn-outline-secondary ms-2">
          Keeper Logs
        </Link>
        {isAdmin && (
          <Button className="ms-2" size="sm" variant="outline-secondary" onClick={runTestJob}>
            Test Mutations
          </Button>
        )}
      </div>
      {missingSuggestions && (
        <Alert variant="warning" className="mb-3">
          No suggestions available. Run <code>generate_missing_mutations</code> or
          click “Auto-Suggest Missing Labels.”
          <AutoSuggestButton
            className="ms-2"
            assistant={searchParams.get("assistant")}
            onComplete={reload}
          />
        </Alert>
      )}
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Original Term</th>
            <th>Suggested Replacement</th>
            <th>Source</th>
            <th>Fallback Count</th>
            <th>Score Before</th>
            <th>Score After</th>
            <th>Δ</th>
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
              <td>{m.mutation_score_before?.toFixed(2)}</td>
              <td>{m.mutation_score_after?.toFixed(2)}</td>
              <td>
                {m.mutation_score_delta != null && (
                  <span
                    className={
                      m.mutation_score_delta > 0
                        ? "badge bg-success"
                        : "badge bg-danger"
                    }
                  >
                    {m.mutation_score_delta.toFixed(2)}
                  </span>
                )}
              </td>
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
              <td colSpan="9" className="text-muted">
                No viable fallback labels were detected from memory anchors. Try
                ingesting more documents or reviewing recent assistant
                reflections.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
