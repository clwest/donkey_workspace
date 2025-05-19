import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Card } from "react-bootstrap";
import apiFetch from "../../utils/apiClient";
import PrimaryStar from "../../components/assistant/PrimaryStar";

export default function AssistantControlPanel() {
  const { slug } = useParams();
  const [assistant, setAssistant] = useState(null);
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await apiFetch(`/assistants/${slug}/`);
        setAssistant(data);

        const [thoughtRes, reflectionRes, delegationRes] = await Promise.all([
          apiFetch(`/assistants/${slug}/thoughts/recent/`).catch(() => ({ thoughts: [] })),
          apiFetch(`/assistants/${slug}/reflections/recent/`).catch(() => ({ thoughts: [] })),
          apiFetch(`/assistants/${slug}/delegations/`).catch(() => ([])),
        ]);

        const items = [];
        if (thoughtRes.thoughts) {
          items.push(
            ...thoughtRes.thoughts.map((t) => ({
              type: "thought",
              content: t.content || t.thought,
              created_at: t.timestamp || t.created_at,
            }))
          );
        }
        if (reflectionRes.thoughts) {
          items.push(
            ...reflectionRes.thoughts.map((r) => ({
              type: "reflection",
              content: r.content,
              created_at: r.timestamp,
            }))
          );
        }
        if (Array.isArray(delegationRes)) {
          items.push(
            ...delegationRes.map((d) => ({
              type: "delegation",
              parent: d.parent,
              child: d.child,
              reason: d.reason,
              summary: d.summary,
              created_at: d.created_at,
            }))
          );
        }
        items.sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        setFeed(items);
      } catch (err) {
        console.error("Failed to load assistant:", err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [slug]);

  const handleReflectNow = async () => {
    try {
      await apiFetch(`/assistants/${slug}/reflect-now/`, { method: "POST" });
    } catch (err) {
      console.error("Reflect failed", err);
    }
  };

  if (loading) return <div className="container my-5">Loading...</div>;
  if (!assistant) return <div className="container my-5">Assistant not found.</div>;

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
          <button className="btn btn-outline-info" onClick={handleReflectNow}>
            Reflect Now
          </button>
          <Link to={`/assistants/${slug}/chat`} className="btn btn-outline-primary">
            Open Chat
          </Link>
          <Link to="/assistants/projects/create" className="btn btn-outline-success">
            Start Task
          </Link>
          <button className="btn btn-outline-danger" onClick={() => alert("Archive not implemented")}>Archive Assistant</button>
        </div>
      </div>

      <div className="row g-4">
        <div className="col-lg-4">
          <Card className="mb-4 h-100 shadow-sm">
            <Card.Header>Overview</Card.Header>
            <Card.Body>
              <p><strong>Tone:</strong> {assistant.tone || "-"}</p>
              <p><strong>Model:</strong> {assistant.preferred_model || "-"}</p>
              <p><strong>Personality:</strong> {assistant.personality || "-"}</p>
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
                  {project.objectives?.length > 0 ? (
                    <ul className="list-group mb-3">
                      {project.objectives.map((obj) => (
                        <li key={obj.id} className="list-group-item">
                          {obj.is_completed ? "✅" : "🔹"} {obj.title}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted">No objectives yet.</p>
                  )}
                  <div className="d-flex gap-2">
                    <Link
                      to={`/assistants/projects/${project.id}/objectives`}
                      className="btn btn-sm btn-outline-primary"
                    >
                      Add Objective
                    </Link>
                    <button className="btn btn-sm btn-outline-info" onClick={handleReflectNow}>
                      Reflect
                    </button>
                  </div>
                </>
              ) : (
                <p className="text-muted">No project assigned.</p>
              )}
            </Card.Body>
          </Card>

          <Card className="shadow-sm">
            <Card.Header>Thought Feed</Card.Header>
            <Card.Body>
              {feed.length === 0 ? (
                <p className="text-muted">No activity yet.</p>
              ) : (
                <ul className="list-group">
                  {feed.map((item, idx) => (
                    <li key={idx} className="list-group-item">
                      {item.type === "delegation" ? (
                        <>
                          <strong>Delegation:</strong> {item.parent} ➡ {item.child}
                          <br />
                          <small>{item.reason}</small>
                        </>
                      ) : item.type === "reflection" ? (
                        <>
                          <strong>Reflection:</strong> {item.content}
                        </>
                      ) : (
                        <>
                          <strong>Thought:</strong> {item.content}
                        </>
                      )}
                      <div className="text-muted small">
                        {new Date(item.created_at).toLocaleString()}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </Card.Body>
          </Card>
        </div>
      </div>
    </div>
  );
}
