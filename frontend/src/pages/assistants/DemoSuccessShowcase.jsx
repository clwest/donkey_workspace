import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import AssistantCard from "@/components/assistant/AssistantCard";

export default function DemoSuccessShowcase() {
  const [assistants, setAssistants] = useState(null);

  useEffect(() => {
    apiFetch("/assistants/demo_success/")
      .then((data) => setAssistants(Array.isArray(data) ? data : []))
      .catch(() => setAssistants([]));
  }, []);

  if (assistants === null) {
    return <div className="container py-5">Loading...</div>;
  }

  return (
    <div className="container py-5">
      <h1 className="mb-4">Demo Success Stories</h1>
      <div className="row">
        {assistants.map((a) => (
          <div key={a.slug} className="col-md-4 mb-4">
            <AssistantCard assistant={a} chatLink={`/assistants/${a.slug}/chat`} />
            <div className="small text-muted mt-1">
              Sessions: {a.sessions} · Messages: {a.messages}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 d-flex gap-2">
        <Link to="/assistants-demos" className="btn btn-outline-secondary">
          Try a Demo
        </Link>
        <Link to="/assistants/create" className="btn btn-primary">
          Create Your Own
        </Link>
      </div>
    </div>
  );
}
