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

  useEffect(() => {
    fetchStabilizationCampaigns()
      .then((list) => {
        const found = list.find((c) => String(c.id) === campaignId);
        setCampaign(found || null);
      })
      .catch(() => setCampaign(null));
  }, [campaignId]);

  const finalize = () => {
    finalizeStabilizationCampaign(campaignId)
      .then(setFinalized)
      .catch(() => {});
  };

  if (!campaign) return <p className="m-4">Loading...</p>;

  return (
    <div className="container my-4">
      <h1 className="mb-3">Stabilization Campaign</h1>
      <pre className="bg-light p-2 rounded mb-3">
        {JSON.stringify(campaign, null, 2)}
      </pre>
      {finalized && (
        <pre className="bg-light p-2 rounded mb-3">
          {JSON.stringify(finalized, null, 2)}
        </pre>
      )}
      <button className="btn btn-primary" onClick={finalize}>
        Finalize Campaign
      </button>
    </div>
  );
}
