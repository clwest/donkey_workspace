import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import AssistantTrustPanel from "@/components/assistant/AssistantTrustPanel";
import apiFetch from "@/utils/apiClient";

export default function TrustProfilePage() {
  const { slug } = useParams();
  const [assistant, setAssistant] = useState(null);

  useEffect(() => {
    apiFetch(`/assistants/${slug}/`).then(setAssistant).catch(() => {});
  }, [slug]);

  if (!assistant) return <div className="container my-5">Loading...</div>;
  return (
    <div className="container my-5" id="trust-panel">
      <h1 className="mb-3">{assistant.name} Trust Profile</h1>
      <AssistantTrustPanel slug={slug} />
    </div>
  );
}
