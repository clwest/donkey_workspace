import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import { Button } from "react-bootstrap";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function AnchorSuggestionPage() {
  useAuthGuard();
  const [rows, setRows] = useState([]);
  const [assistants, setAssistants] = useState([]);
  const [assistant, setAssistant] = useState("");
  const [status, setStatus] = useState("pending");

  const load = async () => {
    const params = new URLSearchParams();
    if (assistant) params.set("assistant", assistant);
    if (status) params.set("status", status);
    const res = await apiFetch(`/anchor/suggestions/?${params.toString()}`);
    setRows(res.results || res);
  };

  useEffect(() => {
    apiFetch("/assistants/").then((res) => setAssistants(res.results || res));
  }, []);

  useEffect(() => {
    load();
  }, [assistant, status]);

  const handleAccept = async (id) => {
    await apiFetch(`/anchor/suggestions/${id}/accept/`, { method: "POST" });
    load();
  };
  const handleReject = async (id) => {
    await apiFetch(`/anchor/suggestions/${id}/reject/`, { method: "POST" });
    load();
  };

  return (
    <div className="container my-4">
      <h2 className="mb-3">Anchor Suggestions</h2>
      <div className="d-flex gap-2 mb-3">
        <select
          className="form-select form-select-sm"
          style={{ maxWidth: "200px" }}
          value={assistant}
          onChange={(e) => setAssistant(e.target.value)}
        >
          <option value="">All Assistants</option>
          {assistants.map((a) => (
            <option key={a.slug} value={a.slug}>
              {a.name}
            </option>
          ))}
        </select>
        <select
          className="form-select form-select-sm"
          style={{ maxWidth: "160px" }}
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">All Status</option>
          <option value="pending">pending</option>
          <option value="accepted">accepted</option>
          <option value="rejected">rejected</option>
        </select>
      </div>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Term</th>
            <th>Context</th>
            <th>Fallback</th>
            <th>Match</th>
            <th>Assistant</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{r.term}</td>
              <td>{r.context?.slice(0, 40)}...</td>
              <td>{r.fallback_score ?? "-"}</td>
              <td>{r.match_strength ?? "-"}</td>
              <td>{r.assistant_slug || ""}</td>
              <td>{r.status}</td>
              <td>
                {r.status === "pending" && (
                  <>
                    <Button
                      size="sm"
                      className="me-1"
                      onClick={() => handleAccept(r.id)}
                    >
                      ✓
                    </Button>
                    <Button
                      size="sm"
                      variant="danger"
                      onClick={() => handleReject(r.id)}
                    >
                      ✗
                    </Button>
                  </>
                )}
              </td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td colSpan="7" className="text-muted">
                No suggestions
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
