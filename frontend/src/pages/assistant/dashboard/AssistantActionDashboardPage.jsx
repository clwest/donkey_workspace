import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { OverlayTrigger, Popover } from "react-bootstrap";
import { toast } from "react-toastify";
import {
  fetchAssistantDashboard,
  reflectOnChat,
  retryBirthReflection,
} from "../../../api/assistants";
import useTourActivation from "../../../hooks/useTourActivation";

export default function AssistantActionDashboardPage() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [insight, setInsight] = useState(null);
  const [reflecting, setReflecting] = useState(false);
  const [retrying, setRetrying] = useState(false);
  const tour = useTourActivation(slug);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetchAssistantDashboard(slug);
        setData(res);
      } catch (err) {
        console.error("Failed to load dashboard", err);
      } finally {
        setLoading(false);
      }
    }
    if (slug) load();
  }, [slug]);

  const triggerReflection = async () => {
    setReflecting(true);
    try {
      const res = await reflectOnChat(slug);
      setInsight(res);
      toast.success("Reflection generated");
    } catch (err) {
      toast.error("Reflection failed");
    } finally {
      setReflecting(false);
    }
  };

  const triggerRetry = async () => {
    setRetrying(true);
    try {
      await retryBirthReflection(slug);
      toast.success("Reflection retried");
      const res = await fetchAssistantDashboard(slug);
      setData(res);
    } catch (err) {
      toast.error("Retry failed");
    } finally {
      setRetrying(false);
    }
  };

  if (loading || tour.loading)
    return <div className="container my-5">Loading...</div>;
  if (!data) return <div className="container my-5">No data.</div>;

  const { assistant, project, tasks, next_actions, thoughts, reflections, documents, recent_memories } = data;
  const intro = recent_memories?.find((m) => m.type === "assistant_intro");

  return (
    <div className="container my-5">
      <h1 className="mb-2">
        {assistant.name} Dashboard
        {assistant.reflection_error && (
          <span className="badge bg-warning text-dark ms-2" title={assistant.reflection_error}>
            ⚠️ Reflection skipped — LLM connection failed
          </span>
        )}
      </h1>
      <div className="text-muted mb-3">
        World: {assistant.specialty} | Archetype: {assistant.archetype}
      </div>
      {intro && (
        <div className="alert alert-success">{intro.content_preview}</div>
      )}
      {(assistant.system_prompt_slug || assistant.system_prompt_id) && (
        <Link
          to={`/prompts/${assistant.system_prompt_slug || assistant.system_prompt_id}`}
          className="btn btn-sm btn-outline-secondary mb-3"
        >
          Edit System Prompt
        </Link>
      )}
      <button
        className="btn btn-sm btn-primary mb-3 ms-2"
        onClick={triggerReflection}
        disabled={reflecting}
      >
        {reflecting ? "Reflecting..." : "Reflect on recent chats"}
      </button>
      {assistant.birth_reflection_retry_count > 0 && (
        <span
          className={`badge ms-2 ${assistant.last_reflection_successful ? "bg-success" : "bg-danger"}`}
        >
          {assistant.birth_reflection_retry_count}
        </span>
      )}
      {assistant.reflection_error && assistant.can_retry_birth_reflection && (
        <OverlayTrigger
          trigger="click"
          placement="bottom"
          overlay={
            <Popover>
              <Popover.Body>
                <div className="d-grid gap-2">
                  <Link
                    to={`/assistants/${slug}/reflections`}
                    className="btn btn-sm btn-outline-secondary"
                  >
                    View Retry Log
                  </Link>
                  <button
                    className="btn btn-sm btn-danger"
                    onClick={triggerRetry}
                    disabled={retrying}
                  >
                    {retrying ? "Retrying..." : "Trigger Retry"}
                  </button>
                </div>
              </Popover.Body>
            </Popover>
          }
          rootClose
        >
          <button className="btn btn-sm btn-outline-danger mb-3 ms-2">
            Retry Options
          </button>
        </OverlayTrigger>
      )}
      {insight && (
        <div className="alert alert-info mt-3">{insight.summary}</div>
      )}
      {project && <h4>Current Project: {project.title}</h4>}

      {tasks && tasks.length > 0 && (
        <>
          <h5 className="mt-4">Tasks</h5>
          <ul className="list-group mb-3">
            {tasks.map((t) => (
              <li key={t.id} className="list-group-item">
                {t.title} <span className="badge bg-secondary ms-2">{t.status}</span>
              </li>
            ))}
          </ul>
        </>
      )}

      {next_actions && next_actions.length > 0 && (
        <>
          <h5>Next Actions</h5>
          <ul className="list-group mb-3">
            {next_actions.map((a) => (
              <li key={a.id} className="list-group-item">
                {a.content}
                {a.assigned_agent_name && (
                  <span className="text-muted ms-2">({a.assigned_agent_name})</span>
                )}
                <span className="badge bg-secondary ms-2">{a.status}</span>
              </li>
            ))}
          </ul>
        </>
      )}

      {thoughts && thoughts.length > 0 && (
        <>
          <h5>Recent Thoughts</h5>
          <ul className="list-group mb-3">
            {thoughts.map((t) => (
              <li key={t.id} className="list-group-item">
                {t.thought}
              </li>
            ))}
          </ul>
        </>
      )}

      {reflections && reflections.length > 0 && (
        <>
          <h5>Recent Reflections</h5>
          <ul className="list-group mb-3">
            {reflections.map((r) => (
              <li key={r.id} className="list-group-item">
                {r.title} - {r.summary}
              </li>
            ))}
          </ul>
        </>
      )}

      {documents && documents.length > 0 && (
        <>
          <h5>Linked Documents</h5>
          <ul className="list-group">
            {documents.map((d) => (
              <li
                key={d.id}
                className="list-group-item d-flex justify-content-between align-items-center"
              >
                <span>
                  {d.title} ({d.source_type})
                </span>
                <span className="badge bg-info text-dark">
                  {d.embedded_percent}%
                </span>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
