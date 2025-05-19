import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card, Table } from "react-bootstrap";
import apiFetch from "../../utils/apiClient";

export default function PrimaryAssistantDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/assistants/primary/");
        setData(res);
      } catch (err) {
        setError(true);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleReflect = async () => {
    try {
      await apiFetch("/assistants/primary/reflect/", { method: "POST" });
    } catch (err) {
      console.error("Reflect failed", err);
    }
  };

  if (loading) return <div className="container my-5">Loading...</div>;
  if (error || !data) return <div className="container my-5">Failed to load.</div>;

  const project = data.projects?.[0];

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">{data.name}</h2>
        <div className="btn-group">
          <button className="btn btn-outline-info" onClick={handleReflect}>
            Reflect Now
          </button>
          <Link to="/assistants/projects/create" className="btn btn-outline-success">
            Start Task
          </Link>
        </div>
      </div>

      <div className="row g-4">
        <div className="col-lg-4">
          <Card className="shadow-sm mb-4">
            <Card.Header>Overview</Card.Header>
            <Card.Body>
              <p><strong>Tone:</strong> {data.tone || "-"}</p>
              <p><strong>Model:</strong> {data.preferred_model || "-"}</p>
              <p><strong>Personality:</strong> {data.personality || "-"}</p>
              {data.system_prompt && (
                <div className="mt-3">
                  <h6>System Prompt</h6>
                  <p className="small text-muted">
                    {data.system_prompt.slice(0, 200)}
                    {data.system_prompt.length > 200 ? "..." : ""}
                  </p>
                </div>
              )}
            </Card.Body>
          </Card>

          {project && (
            <Card className="shadow-sm">
              <Card.Header>Project Summary</Card.Header>
              <Card.Body>
                <h6>
                  <Link to={`/assistants/projects/${project.id}`}>{project.title}</Link>
                </h6>
                {project.objectives?.length > 0 ? (
                  <ul className="list-group mb-2">
                    {project.objectives.map((obj) => (
                      <li key={obj.id} className="list-group-item">
                        {obj.is_completed ? "✅" : "🔹"} {obj.title}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-muted">No objectives.</p>
                )}
              </Card.Body>
            </Card>
          )}
        </div>

        <div className="col-lg-8">
          <Card className="mb-4 shadow-sm">
            <Card.Header>Recent Thoughts</Card.Header>
            <Card.Body>
              {data.recent_thoughts && data.recent_thoughts.length > 0 ? (
                <ul className="list-group">
                  {data.recent_thoughts.map((t, idx) => (
                    <li key={idx} className="list-group-item">
                      {t.thought || t.content}
                      <div className="text-muted small">
                        {new Date(t.created_at || t.timestamp).toLocaleString()}
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted">No recent thoughts.</p>
              )}
            </Card.Body>
          </Card>

          <Card className="shadow-sm">
            <Card.Header>Recent Delegations</Card.Header>
            <Card.Body>
              {data.recent_delegations && data.recent_delegations.length > 0 ? (
                <Table responsive size="sm">
                  <thead>
                    <tr>
                      <th>Delegation</th>
                      <th>Reason</th>
                      <th>Summary</th>
                      <th>Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.recent_delegations.map((d, idx) => (
                      <tr key={idx}>
                        <td>{d.parent} → {d.child}</td>
                        <td>{d.reason}</td>
                        <td>{d.summary || "-"}</td>
                        <td>{new Date(d.created_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <p className="text-muted">No recent delegations.</p>
              )}
            </Card.Body>
          </Card>
        </div>
      </div>
    </div>
  );
}
