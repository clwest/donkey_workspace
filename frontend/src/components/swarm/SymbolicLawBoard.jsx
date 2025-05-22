import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SymbolicLawBoard() {
  const [laws, setLaws] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/symbolic-laws/");
        setLaws(res.results || res);
      } catch (err) {
        console.error("Failed to load laws", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Symbolic Laws</h5>
      <ul className="list-group">
        {laws.map((l) => (
          <li key={l.id} className="list-group-item">
            <strong>{l.enforcement_scope}</strong> – {l.description}
          </li>
        ))}
        {laws.length === 0 && (
          <li className="list-group-item text-muted">No laws recorded.</li>
        )}
      </ul>
    </div>
  );
}
