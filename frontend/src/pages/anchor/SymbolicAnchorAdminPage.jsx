import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function SymbolicAnchorAdminPage() {
  useAuthGuard();
  const [anchors, setAnchors] = useState([]);
  const [savingId, setSavingId] = useState(null);
  const [searchParams] = useSearchParams();
  const [query, setQuery] = useState("");
  const [orderBy, setOrderBy] = useState("label");

  useEffect(() => {
    const assistant = searchParams.get("assistant");
    const params = new URLSearchParams();
    if (assistant) params.set("assistant", assistant);
    if (query) params.set("q", query);
    if (orderBy) params.set("order_by", orderBy);
    params.set("show_empty", "true");
    const url = `/memory/glossary/anchors/?${params.toString()}`;
    const t = setTimeout(() => {
      apiFetch(url)
        .then((d) => setAnchors(d.results || d))
        .catch(() => setAnchors([]));
    }, 300);
    return () => clearTimeout(t);
  }, [searchParams, query, orderBy]);

  const handleChange = (id, value) => {
    setAnchors(
      anchors.map((a) => (a.id === id ? { ...a, explanation: value } : a))
    );
  };

  const toggleProtected = async (id) => {
    const anchor = anchors.find((a) => a.id === id);
    await apiFetch(`/memory/symbolic-anchors/${id}/`, {
      method: "PATCH",
      body: { protected: !anchor.protected },
    });
    setAnchors(
      anchors.map((a) =>
        a.id === id ? { ...a, protected: !a.protected } : a
      )
    );
  };

  const saveGuidance = async (id) => {
    const anchor = anchors.find((a) => a.id === id);
    setSavingId(id);
    await apiFetch(`/memory/symbolic-anchors/${id}/`, {
      method: "PATCH",
      body: { explanation: anchor.explanation },
    });
    setSavingId(null);
  };

  return (
    <div className="container my-4">
      <h1 className="mb-3">Glossary Anchor Admin</h1>
      <div className="mb-3 d-flex gap-2">
        <input
          className="form-control"
          placeholder="Search anchors..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select
          className="form-select w-auto"
          value={orderBy}
          onChange={(e) => setOrderBy(e.target.value)}
        >
          <option value="label">Label A-Z</option>
          <option value="-label">Label Z-A</option>
          <option value="-fallback_score">Fallback Score ↓</option>
          <option value="fallback_score">Fallback Score ↑</option>
          <option value="-last_used_in_reflection">Last Used ↓</option>
          <option value="last_used_in_reflection">Last Used ↑</option>
        </select>
      </div>
      <ul className="list-group">
        {anchors.map((a) => (
          <li key={a.id} className="list-group-item">
            <strong dangerouslySetInnerHTML={{
              __html: query
                ? a.label.replace(new RegExp(`(${query})`, 'i'), '<b>$1</b>')
                : a.label,
            }} /> ({a.slug})
            <div className="mt-1">
              <a href={`/anchor/symbolic/${a.slug}`}>View Training</a>
            </div>
            <div className="small text-muted">
              Last Fallback: {a.last_fallback || "-"} | Uses: {a.total_uses} |
              Avg Score: {a.avg_score?.toFixed?.(2) || "0"}
            </div>
            <div className="form-check mt-1">
              <input
                className="form-check-input"
                type="checkbox"
                checked={a.protected || false}
                onChange={() => toggleProtected(a.id)}
                id={`prot-${a.id}`}
              />
              <label className="form-check-label" htmlFor={`prot-${a.id}`}>Protect Anchor</label>
            </div>
            <textarea
              className="form-control mt-2"
              rows={2}
              value={a.explanation || ""}
              onChange={(e) => handleChange(a.id, e.target.value)}
            />
            <button
              className="btn btn-primary btn-sm mt-1"
              onClick={() => saveGuidance(a.id)}
              disabled={savingId === a.id}
            >
              {savingId === a.id ? "Saving..." : "Save"}
            </button>
          </li>
        ))}
        {anchors.length === 0 && (
          <li className="list-group-item text-muted">No anchors found.</li>
        )}
      </ul>
    </div>
  );
}
