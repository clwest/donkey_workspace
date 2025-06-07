import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import apiFetch from "@/utils/apiClient";

export default function AssistantTrailRecap() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

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
    <div className="container my-5">
      <h1 className="mb-3">Journey Recap 📜</h1>
      {data.trail_summary && (
        <p className="lead">{data.trail_summary}</p>
      )}
      <ul className="list-group mb-4">
        {data.trail_markers.map((m, idx) => (
          <li key={idx} className="list-group-item">
            <strong>{m.marker_type}</strong> – {new Date(m.timestamp).toLocaleString()}
            {m.notes && <span className="ms-2 text-muted">{m.notes}</span>}
          </li>
        ))}
      </ul>
      <button className="btn btn-primary" onClick={handleContinue}>
        Continue
      </button>
    </div>
  );
}
