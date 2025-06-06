import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Button } from "react-bootstrap";
import { toast } from "react-toastify";
import apiFetch from "../../../utils/apiClient";

export default function AssistantReflectionLogsPage() {
  const { slug } = useParams();
  const [logs, setLogs] = useState([]);
  const [latestReplay, setLatestReplay] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchLogs() {
      try {
        const data = await apiFetch(`/assistants/${slug}/reflections/`);
        setLogs(data);
      } catch (err) {
        console.error("Failed to load reflections", err);
      }
    }
    async function fetchLatestReplay() {
      try {
        const data = await apiFetch(`/assistants/${slug}/replays/`);
        setLatestReplay(data[0] || null);
      } catch (err) {
        console.error("Failed to load replays", err);
      }
    }
    fetchLogs();
    fetchLatestReplay();
  }, [slug]);

  const createObjective = async (id) => {
    try {
      await apiFetch(`/assistants/${slug}/objectives/from-reflection/`, {
        method: "POST",
        body: { reflection_id: id },
      });
      toast.success("Objective created from reflection!");
      navigate(`/assistants/${slug}/objectives/`);
    } catch (err) {
      toast.error("Failed to create objective");
    }
  };

  const replayReflection = async (id) => {
    try {
      await apiFetch(`/reflections/${id}/replay/`, { method: "POST" });
      toast.success("Reflection replayed!");
      navigate(`/assistants/${slug}/replays`);
    } catch (err) {
      toast.error("Failed to replay reflection");
    }
  };

  return (
    <div className="container my-5">
      <h2 className="mb-4">🪞 Reflections for {slug}</h2>
      <Link
        to={`/assistants/${slug}/replays`}
        className="btn btn-sm btn-outline-primary mb-3"
      >
        🌀 Replay Reflections
      </Link>
      <Button
        className="mb-4"
        onClick={() => navigate(`/assistants/${slug}/replays`)}
      >
        View Replays
      </Button>
      {latestReplay && (
        <div className="mb-3">
          <Link
            to={`/assistants/${slug}/rag_playback/${latestReplay.rag_playback}`}
            className="btn btn-sm btn-outline-info me-2"
          >
            View Latest RAG Playback
          </Link>
          <Link
            to={`/assistants/${slug}/rag_playback/compare/${latestReplay.id}`}
            className="btn btn-sm btn-outline-primary"
          >
            Compare Playback
          </Link>
        </div>
      )}
      {logs.length === 0 ? (
        <p>No reflections found.</p>
      ) : (
        <ul className="list-group mb-3">
          {logs.map((r) => (
            <li
              key={r.id}
              className="list-group-item d-flex justify-content-between align-items-start"
            >
              <div>
                <strong>{r.title || r.summary.slice(0, 40)}</strong>
                <br />
                <small className="text-muted">
                  {new Date(r.created_at).toLocaleString()}
                </small>
              </div>
              <div>
                <button
                  className="btn btn-sm btn-outline-info me-2"
                  onClick={() => replayReflection(r.id)}
                >
                  🔄 Replay
                </button>
                <button
                  className="btn btn-sm btn-outline-primary"
                  onClick={() => createObjective(r.id)}
                >
                  ➕ Create Objective
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
      <Link to={`/assistants/${slug}`} className="btn btn-outline-secondary">
        🔙 Back to Assistant
      </Link>
    </div>
  );
}
