import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, Table } from "react-bootstrap";
import apiFetch from "../../utils/apiClient";
import ReflectNowButton from "../../components/assistant/ReflectNowButton";

export default function AssistantSessionDashboardPage() {
  const { slug } = useParams();

  const [sessions, setSessions] = useState([]);
  const [sessionsLoading, setSessionsLoading] = useState(true);
  const [sessionsError, setSessionsError] = useState(null);

  const [delegations, setDelegations] = useState([]);
  const [delegationsLoading, setDelegationsLoading] = useState(true);
  const [delegationsError, setDelegationsError] = useState(null);

  const [reflections, setReflections] = useState([]);
  const [reflectionsLoading, setReflectionsLoading] = useState(true);
  const [reflectionsError, setReflectionsError] = useState(null);

  useEffect(() => {
    async function fetchSessions() {
      try {
        const data = await apiFetch(`/assistants/${slug}/sessions/`);
        setSessions(data.sessions || []);
      } catch (err) {
        setSessionsError(true);
      } finally {
        setSessionsLoading(false);
      }
    }

    async function fetchDelegations() {
      try {
        const data = await apiFetch(`/assistants/${slug}/delegations/`);
        setDelegations(data || []);
      } catch (err) {
        setDelegationsError(true);
      } finally {
        setDelegationsLoading(false);
      }
    }

    async function fetchReflections() {
      try {
        const data = await apiFetch(`/assistants/${slug}/reflections/`);
        setReflections(data || []);
      } catch (err) {
        setReflectionsError(true);
      } finally {
        setReflectionsLoading(false);
      }
    }

    fetchSessions();
    fetchDelegations();
    fetchReflections();
  }, [slug]);

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">Assistant Dashboard: {slug}</h2>
        <div className="btn-group">
          <ReflectNowButton slug={slug} />
          <Link to={`/assistants/${slug}`} className="btn btn-outline-secondary">
            Back to Assistant
          </Link>
        </div>
      </div>

      <div className="d-grid gap-4">
        <Card className="shadow-sm">
          <Card.Header>{"\u{1F5E3}\uFE0F"} Recent Sessions</Card.Header>
          <Card.Body>
            {sessionsLoading && <p>Loading...</p>}
            {sessionsError && <p className="text-danger">Error fetching data</p>}
            {!sessionsLoading && !sessionsError && sessions.length === 0 && (
              <p>No sessions found.</p>
            )}
            {!sessionsLoading && !sessionsError && sessions.length > 0 && (
              <Table responsive>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Session ID</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {sessions.map((s) => (
                    <tr key={s.session_id}>
                      <td>{new Date(s.created_at).toLocaleString()}</td>
                      <td>{s.session_id}</td>
                      <td>
                        <button className="btn btn-sm btn-outline-primary">
                          View Transcript
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            )}
          </Card.Body>
        </Card>

        <Card className="shadow-sm">
          <Card.Header>{"\u{1F9EA}"} Delegation History</Card.Header>
          <Card.Body>
            {delegationsLoading && <p>Loading...</p>}
            {delegationsError && <p className="text-danger">Error fetching data</p>}
            {!delegationsLoading && !delegationsError && delegations.length === 0 && (
              <p>No delegation events.</p>
            )}
            {!delegationsLoading && !delegationsError && delegations.length > 0 && (
              <Table responsive>
                <thead>
                  <tr>
                    <th>Parent ➡ Child</th>
                    <th>Reason</th>
                    <th>Summary</th>
                  </tr>
                </thead>
                <tbody>
                  {delegations.map((d, idx) => (
                    <tr key={idx}>
                      <td>
                        <Link to={`/assistants/${d.parent}`}>{d.parent}</Link> ➡{' '}
                        <Link to={`/assistants/${d.child}`}>{d.child}</Link>
                      </td>
                      <td>{d.reason}</td>
                      <td>{d.summary || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            )}
          </Card.Body>
        </Card>

        <Card className="shadow-sm">
          <Card.Header>{"\u{1F4AD}"} Reflections</Card.Header>
          <Card.Body>
            {reflectionsLoading && <p>Loading...</p>}
            {reflectionsError && <p className="text-danger">Error fetching data</p>}
            {!reflectionsLoading && !reflectionsError && reflections.length === 0 && (
              <p>No reflections available.</p>
            )}
            {!reflectionsLoading && !reflectionsError && reflections.length > 0 && (
              <ul className="list-group">
                {reflections.map((r) => (
                  <li key={r.id || r.timestamp} className="list-group-item">
                    <div className="d-flex justify-content-between">
                      <span>{new Date(r.created_at || r.timestamp).toLocaleString()}</span>
                    </div>
                    <p className="mb-1">{r.content || r.summary || r.thought}</p>
                    {r.tags && r.tags.length > 0 && (
                      <div className="mt-2">
                        {r.tags.map((tag) => (
                          <span key={tag} className="badge bg-secondary me-2">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </Card.Body>
        </Card>
      </div>
    </div>
  );
}
