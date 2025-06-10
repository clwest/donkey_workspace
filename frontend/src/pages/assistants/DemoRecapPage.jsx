import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import DemoOverlayPanel from "@/components/demo/DemoOverlayPanel";
import AssistantTrustPanel from "@/components/assistant/AssistantTrustPanel";
import GrowthTrackPanel from "@/components/assistant/GrowthTrackPanel";

export default function DemoRecapPage() {
  const { slug, sessionId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch(`/assistants/demo_recap/${sessionId}/`)
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [sessionId]);

  return (
    <div className="container my-5" id="demo-recap-page">
      <h1 className="mb-3">Demo Recap</h1>
      {loading && <p>Loading recap...</p>}
      {!loading && data && (
        <div className="mb-3">
          <p>Messages Sent: {data.messages_sent}</p>
          <p>Helpful Tips: {data.tips_helpful}</p>
          <p>Score: {data.score}</p>
          {data.starter_query && <p>Starter: {data.starter_query}</p>}
        </div>
      )}
      <div className="mb-3">
        <Link
          to={`/assistants/${slug}/demo_overlay/`}
          className="btn btn-outline-secondary me-2 btn-sm"
        >
          View Overlay
        </Link>
        <Link
          to={`/assistants/${slug}/demo_replay/${sessionId}`}
          className="btn btn-outline-secondary btn-sm"
        >
          View Replay
        </Link>
      </div>
      <DemoOverlayPanel slug={slug} sessionId={sessionId} />
      <AssistantTrustPanel slug={slug} />
      <GrowthTrackPanel slug={slug} />
    </div>
  );
}
