import { useEffect, useState } from "react";
import useRealtimeAssistant from "../../hooks/useRealtimeAssistant";
import { useParams } from "react-router-dom";
import {
  fetchStabilizationCampaigns,
  finalizeStabilizationCampaign,
} from "../../api/ontology";
import { fetchSymbolicReflections } from "../../api/memories";

export default function StabilizationCampaignDetailPage() {
  const { campaignId } = useParams();
  const [campaign, setCampaign] = useState(null);
  const [finalized, setFinalized] = useState(null);
  const [reflections, setReflections] = useState([]);
  const [loading, setLoading] = useState(true);
  const realtime = useRealtimeAssistant();

  useEffect(() => {
    setLoading(true);
    fetchStabilizationCampaigns()
      .then((list) => {
        const found = list.find((c) => String(c.id) === campaignId);
        setCampaign(found || null);
        setLoading(false);
      })
      .catch(() => {
        setCampaign(null);
        setLoading(false);
      });
    fetchSymbolicReflections({ campaignId }).then(setReflections).catch(() => {});
  }, [campaignId]);

  const finalize = () => {
    realtime.start([{ role: "user", content: `finalize:${campaignId}` }]);
    finalizeStabilizationCampaign(campaignId)
      .then((res) => {
        setFinalized(res);
        if (res.updated) {
          setCampaign((prev) => ({ ...prev, status: "closed" }));
          fetchSymbolicReflections({ campaignId }).then(setReflections).catch(() => {});
        }
      })
      .catch(() => {});
  };

  if (loading) return <p className="m-4">Loading...</p>;
  if (!campaign) return <p className="m-4">Campaign not found.</p>;

  return (
    <div className="container my-4">
      <h1 className="mb-3">Stabilization Campaign</h1>
      <p>
        <strong>Clause:</strong> {campaign.target_clause_id}
      </p>
      <p>
        <strong>Status:</strong> {campaign.status}
      </p>
      {finalized && (
        <p>
          <strong>Symbolic Gain:</strong> {finalized.symbolic_gain.toFixed(2)}
        </p>
      )}

      {finalized && (
        <div className="mb-3">
          <h5>Clause Before</h5>
          <pre className="bg-light p-2 rounded">{finalized.clause_before}</pre>
          <h5>Clause After</h5>
          <pre className="bg-light p-2 rounded">{finalized.clause_after}</pre>
        </div>
      )}

      <button className="btn btn-primary" onClick={finalize}>
        Finalize Campaign
      </button>

      {realtime.streaming && (
        <div className="alert alert-warning mt-3">
          {realtime.output}
          <button
            className="btn btn-sm btn-secondary ms-2"
            onClick={realtime.interrupt}
          >
            Interrupt
          </button>
        </div>
      )}

      {reflections.length > 0 && (
        <div className="alert alert-info mt-4">
          🪞 Reflections Logged – {reflections.length} assistants reflected.
        </div>
      )}

      {reflections.length > 0 && (
        <div className="mt-3" id="reflections">
          <h5>Assistant Reflections</h5>
          <ul className="list-group">
            {reflections.map((r) => (
              <li key={r.id} className="list-group-item">
                <strong>{r.assistant_name || "Assistant"}</strong>
                <div className="small text-muted">
                  {new Date(r.created_at).toLocaleString()}
                </div>
                <p className="mb-0">{r.event}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
