import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Button } from "react-bootstrap";
import { toast } from "react-toastify";
import apiFetch from "../../../utils/apiClient";

export default function AssistantReflectionLogsPage() {
  const { slug } = useParams();
  const [logs, setLogs] = useState([]);
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
    fetchLogs();
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

  return (
    <div className="container my-5">
      <h2 className="mb-4">🪞 Reflections for {slug}</h2>
      <Link
        to={`/assistants/${slug}/replays/`}
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
      {logs.length === 0 ? (
        <p>No reflections found.</p>
      ) : (
        <ul className="list-group mb-3">
          {logs.map((r) => (
            <li key={r.id} className="list-group-item d-flex justify-content-between align-items-start">
              <div>
                <strong>{r.title || r.summary.slice(0, 40)}</strong>
                <br />
                <small className="text-muted">{new Date(r.created_at).toLocaleString()}</small>
              </div>
              <button className="btn btn-sm btn-outline-primary" onClick={() => createObjective(r.id)}>
                ➕ Create Objective
              </button>
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
