import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualComplianceDashboard() {
  const [records, setRecords] = useState([]);

  useEffect(() => {
    apiFetch("/agents/ritual-compliance/")
      .then(setRecords)
      .catch(() => setRecords([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Compliance</h5>
      <ul className="list-group">
        {records.map((r) => (
          <li key={r.id} className="list-group-item">
            <strong>{r.civilization}</strong> - {r.compliance_status}
          </li>
        ))}
        {records.length === 0 && (
          <li className="list-group-item text-muted">No records found.</li>
        )}
      </ul>
    </div>
  );
}
