import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import HintBubble from "../../../components/HintBubble";
import useAssistantHints from "../../../hooks/useAssistantHints";
import apiFetch from "../../../utils/apiClient";
import AssistantCard from "../../../components/assistant/AssistantCard";

export default function AssistantDemoPage() {
  const [assistants, setAssistants] = useState([]);
  const { hints, dismissHint } = useAssistantHints("demo");

  useEffect(() => {
    apiFetch("/assistants/demos/")
      .then((data) => setAssistants(Array.isArray(data) ? data : []))
      .catch((err) => console.error("Failed to fetch demo assistants:", err));
  }, []);

  return (
    <div className="container py-5 position-relative">
      <h1 className="mb-4">🧪 AI Assistant Demos</h1>
      {hints.find((h) => h.id === "demo_intro" && !h.dismissed) && (
        <HintBubble
          label={hints.find((h) => h.id === "demo_intro").label}
          content={hints.find((h) => h.id === "demo_intro").content}
          position={{ top: 60, right: 20 }}
          onDismiss={() => dismissHint("demo_intro")}
        />
      )}
      <div className="row" id="demo-assistant-cards">
        {assistants.map((assistant) => (
          <div key={assistant.id} className="col-md-4 mb-4">
            <AssistantCard
              assistant={assistant}
              demo
              to={`/assistants/${assistant.slug}`}
              chatLink={`/assistants/${assistant.slug}/chat`}
            />
          </div>
        ))}
        {assistants.length === 0 && (
          <p className="text-muted text-center">No demo assistants available yet.</p>
        )}
      </div>
      {hints.find((h) => h.id === "demo_start_chat" && !h.dismissed) && (
        <HintBubble
          label={hints.find((h) => h.id === "demo_start_chat").label}
          content={hints.find((h) => h.id === "demo_start_chat").content}
          highlightSelector="#demo-assistant-cards"
          onDismiss={() => dismissHint("demo_start_chat")}
        />
      )}
    </div>
  );
}
