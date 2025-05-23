import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CognitiveBalanceDashboard() {
  const [reports, setReports] = useState([]);

  useEffect(() => {
    apiFetch("/agents/cognitive-balance/")
      .then(setReports)
      .catch(() => setReports([]));
  }, []);

  return (
    <div className="card my-3">
      <div className="card-header">Cognitive Balance Reports</div>
      <table className="table mb-0">
        <thead>
          <tr>
            <th>Guild</th>
            <th>Entropy</th>
            <th>Recommendations</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((r) => (
            <tr key={r.id}>
              <td>{r.guild.name}</td>
              <td>{r.entropy_index}</td>
              <td>{r.recommendations}</td>
            </tr>
          ))}
          {reports.length === 0 && (
            <tr>
              <td colSpan="3" className="text-muted">
                No reports available.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
