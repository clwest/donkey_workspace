import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function ContinuityAnchorEditor() {
  const [anchors, setAnchors] = useState([]);
  const [label, setLabel] = useState("");

  useEffect(() => {
    apiFetch("/memory/continuity-anchors/")
      .then((d) => setAnchors(d.results || d))
      .catch(() => setAnchors([]));
  }, []);

  const createAnchor = async () => {
    if (!label) return;
    const res = await apiFetch("/memory/continuity-anchors/", {
      method: "POST",
      body: { label },
    });
    setAnchors([res, ...anchors]);
    setLabel("");
  };

  return (
    <div className="my-3">
      <h5>Continuity Anchors</h5>
      <div className="input-group mb-2">
        <input
          type="text"
          className="form-control"
          placeholder="Label"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
        />
        <button className="btn btn-primary" onClick={createAnchor}>
          Add
        </button>
      </div>
      <ul className="list-group">
        {anchors.map((a) => (
          <li key={a.id} className="list-group-item">
            {a.label} — {a.mythic_tag}
          </li>
        ))}
        {anchors.length === 0 && (
          <li className="list-group-item text-muted">No anchors defined.</li>
        )}
      </ul>
    </div>
  );
}
