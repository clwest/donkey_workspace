import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  fetchStabilizationCampaigns,
  finalizeStabilizationCampaign,
} from "../../api/ontology";

export default function StabilizationCampaignDetailPage() {
  const { campaignId } = useParams();
  const [campaign, setCampaign] = useState(null);
  const [finalized, setFinalized] = useState(null);
  const [loading, setLoading] = useState(true);

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
  }, [campaignId]);

  const finalize = () => {
    finalizeStabilizationCampaign(campaignId)
      .then((res) => {
        setFinalized(res);
        if (res.updated) {
          setCampaign((prev) => ({ ...prev, status: "closed" }));
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
    </div>
  );
}
