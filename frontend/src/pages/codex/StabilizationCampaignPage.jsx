import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  startStabilizationCampaign,
  fetchCodexClauses,
} from "../../api/ontology";

export default function StabilizationCampaignPage() {
  const [clauseId, setClauseId] = useState("");
  const [clauses, setClauses] = useState([]);
  const navigate = useNavigate();
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchCodexClauses().then(setClauses).catch(() => {});
  }, []);

  const launch = () => {
    if (!clauseId) return;
    startStabilizationCampaign(clauseId)
      .then((res) => {
        setResult(res);
        if (res.campaign_id) {
          navigate(`/codex/stabilize/${res.campaign_id}`);
        }
      })
      .catch((e) => console.error(e));
  };

  return (
    <div className="container my-4">
      <h1 className="mb-3">Clause Stabilization Campaign</h1>
      <div className="input-group mb-3" style={{ maxWidth: "400px" }}>
        <select
          className="form-select"
          value={clauseId}
          onChange={(e) => setClauseId(e.target.value)}
        >
          <option disabled value="">
            Select a clause
          </option>
          {clauses.map((c) => (
            <option key={c.id} value={c.id}>
              {c.text}
            </option>
          ))}
        </select>
        <button className="btn btn-primary" disabled={!clauseId} onClick={launch}>
          Launch
        </button>
      </div>
      {result && (
        <pre className="bg-light p-2 rounded">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
