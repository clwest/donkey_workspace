import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import TrailMilestoneEditor from "@/components/TrailMilestoneEditor";

export default function AssistantTrailRecap() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null);

  useEffect(() => {
    apiFetch(`/assistants/${slug}/trail/`)
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [slug]);

  const handleContinue = async () => {
    await apiFetch(`/assistants/${slug}/`, {
      method: "PATCH",
      body: { show_trail_recap: false },
    });
    navigate(`/assistants/${slug}`);
  };

  if (loading) return <div className="container my-5">Loading recap...</div>;
  if (!data) return <div className="container my-5">Failed to load recap.</div>;

  return (
    <div className="container my-5" id="trail-page">
      <h1 className="mb-3">Journey Recap 📜</h1>
      {data.trail_summary && (
        <p className="lead">{data.trail_summary}</p>
      )}
      <ul className="list-group mb-4">
        {data.trail_markers.map((m) => (
          <li key={m.id} className="list-group-item">
            <div className="d-flex justify-content-between align-items-start">
              <div>
                <strong>{m.marker_type}</strong> – {new Date(m.timestamp).toLocaleString()}
                {m.notes && <span className="ms-2 text-muted">{m.notes}</span>}
                {m.user_note && <div className="mt-1">{m.user_note}</div>}
              </div>
              <div>
                {m.user_emotion && (
                  <span className="badge bg-secondary me-2">{m.user_emotion}</span>
                )}
                {m.is_starred && <span className="me-2">⭐</span>}
                <button
                  className="btn btn-sm btn-outline-secondary"
                  onClick={() => setEditing(m)}
                >
                  Edit
                </button>
              </div>
            </div>
          </li>
        ))}
      </ul>
      <button className="btn btn-primary" onClick={handleContinue}>
        Continue
      </button>

      {editing && (
        <div className="modal d-block" tabIndex="-1">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Edit Milestone</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setEditing(null)}
                ></button>
              </div>
              <div className="modal-body">
                <TrailMilestoneEditor
                  marker={editing}
                  onSaved={(upd) => {
                    setData({
                      ...data,
                      trail_markers: data.trail_markers.map((t) =>
                        t.id === editing.id ? { ...t, ...upd } : t
                      ),
                    });
                    setEditing(null);
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
