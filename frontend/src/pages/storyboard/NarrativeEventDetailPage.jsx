import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

export default function NarrativeEventDetailPage() {
  const { id } = useParams();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    apiFetch(`/storyboard/${id}/`)
      .then(setEvent)
      .catch((err) => console.error("Failed to load event", err))
      .finally(() => setLoading(false));
  }, [id]);

  async function generateSummary() {
    if (!id) return;
    setSaving(true);
    try {
      const res = await apiFetch(`/mcp/narrative_events/${id}/summarize/`, {
        method: "POST",
      });
      setEvent((prev) => ({ ...prev, scene_summary: res.summary, summary_generated: true }));
    } catch (err) {
      console.error("Failed to summarize", err);
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="container mt-5">Loading...</div>;
  if (!event) return <div className="container mt-5">Event not found.</div>;

  return (
    <div className="container mt-5">
      <h1 className="mb-3">🎬 {event.title}</h1>
      {event.description && <p>{event.description}</p>}
      <div className="card mt-4">
        <div className="card-body">
          <h5 className="card-title">Scene Summary</h5>
          {event.scene_summary ? (
            <p>{event.scene_summary}</p>
          ) : (
            <button className="btn btn-primary" onClick={generateSummary} disabled={saving}>
              {saving ? "Summarizing..." : "🧠 Generate Summary"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
