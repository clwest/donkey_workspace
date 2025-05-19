import { useEffect, useState } from "react";
import PrimaryStar from "../../components/assistant/PrimaryStar";
import apiFetch from "../../utils/apiClient";
import { Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Card } from "react-bootstrap";

export default function PrimaryAssistantPage() {
  const [assistant, setAssistant] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch("/assistants/primary/");
        setAssistant(data);
      } catch (err) {
        console.error("Failed to load primary assistant", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div className="container my-5">Loading...</div>;
  if (error || !assistant)
    return (
      <div className="container my-5">
        No primary assistant has been designated yet. Please configure one to
        serve as your orchestrator.
      </div>
    );

  const doc = assistant.documents?.[0];
  const project = assistant.projects?.[0];

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">
          {assistant.name}
          <PrimaryStar isPrimary={assistant.is_primary} />
        </h2>
        <div className="btn-group">
          <Link to={`/assistants/${assistant.slug}/chat`} className="btn btn-outline-primary">
            Open Chat
          </Link>
        </div>
      </div>

      <div className="row g-4">
        <div className="col-lg-4">
          <Card className="mb-4 h-100 shadow-sm">
            <Card.Header>Overview</Card.Header>
            <Card.Body>
              <p>
                <strong>Tone:</strong> {assistant.tone || "-"}
              </p>
              <p>
                <strong>Model:</strong> {assistant.preferred_model || "-"}
              </p>
              <p>
                <strong>Personality:</strong> {assistant.personality || "-"}
              </p>
              {assistant.is_primary && (
                <p>
                  <strong>Primary Role:</strong> ✅ System Orchestrator
                </p>
              )}
              {assistant.system_prompt && (
                <div className="mt-3">
                  <h6>System Prompt</h6>
                  <ReactMarkdown remarkPlugins={[remarkGfm]} className="markdown">
                    {assistant.system_prompt}
                  </ReactMarkdown>
                </div>
              )}
            </Card.Body>
          </Card>

          {doc && (
            <Card className="shadow-sm">
              <Card.Header>Linked Document</Card.Header>
              <Card.Body>
                <h6>
                  <Link to={`/intel/documents/${doc.id}`}>{doc.title}</Link>
                </h6>
                <p className="small text-muted">{doc.summary || "No summary."}</p>
                {doc.tags?.length > 0 && (
                  <div className="mt-2">
                    {doc.tags.map((tag) => (
                      <span key={tag} className="badge bg-secondary me-2">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </Card.Body>
            </Card>
          )}
        </div>

        <div className="col-lg-8">
          <Card className="mb-4 shadow-sm">
            <Card.Header>Project Overview</Card.Header>
            <Card.Body>
              {project ? (
                <>
                  <h5>
                    <Link to={`/assistants/projects/${project.id}`}>{project.title}</Link>
                  </h5>
                </>
              ) : (
                <p className="text-muted">No project assigned.</p>
              )}
            </Card.Body>
          </Card>
        </div>
      </div>
    </div>
  );
}
