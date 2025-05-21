import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function OntologyAuditPanel() {
  const [audits, setAudits] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/swarm/ontology-audits/");
        setAudits(res.results || res);
      } catch (err) {
        console.error("Failed to load audits", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Ontology Audits</h5>
      <ul className="list-group">
        {audits.map((a) => (
          <li key={a.id} className="list-group-item">
            {a.scope} – paradox rate {a.paradox_rate}
          </li>
        ))}
        {audits.length === 0 && (
          <li className="list-group-item text-muted">No audits recorded.</li>
        )}
      </ul>
    </div>
  );
}
