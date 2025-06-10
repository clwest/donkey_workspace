import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import GrowthTrackPanel from "@/components/assistant/GrowthTrackPanel";
import apiFetch from "@/utils/apiClient";

export default function GrowthPanelPage() {
  const { slug } = useParams();
  const [assistant, setAssistant] = useState(null);

  useEffect(() => {
    apiFetch(`/assistants/${slug}/`).then(setAssistant).catch(() => {});
  }, [slug]);

  if (!assistant) return <div className="container my-5">Loading...</div>;
  return (
    <div className="container my-5" id="growth-panel">
      <h1 className="mb-3">{assistant.name} Growth</h1>
      <GrowthTrackPanel
        slug={slug}
        stage={assistant.growth_stage}
        points={assistant.growth_points}
      />
    </div>
  );
}
