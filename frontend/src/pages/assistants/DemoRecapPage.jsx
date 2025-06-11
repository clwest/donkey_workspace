import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useTranslation } from 'react-i18next';
import apiFetch from "@/utils/apiClient";
import DemoOverlayPanel from "@/components/demo/DemoOverlayPanel";
import AssistantTrustPanel from "@/components/assistant/AssistantTrustPanel";
import GrowthTrackPanel from "@/components/assistant/GrowthTrackPanel";

export default function DemoRecapPage() {
  const { slug, sessionId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { t } = useTranslation();

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
      <h1 className="mb-3">{t('demorecap.title')}</h1>
      {loading && (
        <div className="my-3 text-center">
          <div className="spinner-border" role="status" />
        </div>
      )}
      {!loading && data && (
        <div className="mb-3">
          <p>{t('demorecap.messages')}: {data.messages_sent}</p>
          <p>{t('demorecap.tips')}: {data.tips_helpful}</p>
          <p>{t('demorecap.score')}: {data.score}</p>
          {data.starter_query && <p>{t('demorecap.starter')}: {data.starter_query}</p>}
        </div>
      )}
      <div className="mb-3">
        <Link
          to={`/assistants/${slug}/demo_overlay/`}
          className="btn btn-outline-secondary me-2 btn-sm"
        >
          {t('demorecap.view_overlay')}
        </Link>
        <Link
          to={`/assistants/${slug}/demo_replay/${sessionId}`}
          className="btn btn-outline-secondary btn-sm"
        >
          {t('demorecap.view_replay')}
        </Link>
      </div>
      <DemoOverlayPanel slug={slug} sessionId={sessionId} />
      <AssistantTrustPanel slug={slug} />
      <GrowthTrackPanel slug={slug} />
    </div>
  );
}
