import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchAssistantDashboard } from "../../../api/assistants";

export default function AssistantActionDashboardPage() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

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

  if (loading) return <div className="container my-5">Loading...</div>;
  if (!data) return <div className="container my-5">No data.</div>;

  const { assistant, project, tasks, next_actions, thoughts, reflections, documents } = data;

  return (
    <div className="container my-5">
      <h1 className="mb-4">{assistant.name} Dashboard</h1>
      {assistant.system_prompt_id && (
        <Link
          to={`/prompts/${assistant.system_prompt_id}`}
          className="btn btn-sm btn-outline-secondary mb-3"
        >
          Edit System Prompt
        </Link>
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
