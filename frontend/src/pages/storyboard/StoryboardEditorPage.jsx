import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import NarrativeEventEditor from "../../components/storyboard/NarrativeEventEditor";

export function NarrativeTimeline({ events }) {
  if (!events?.length) return <p>No events.</p>;
  return (
    <div className="timeline">
      {events.map((e) => (
        <div key={e.id} className="card mb-3">
          <div className="card-body">
            <h5 className="card-title">{e.title}</h5>
            {e.description && <p className="card-text">{e.description}</p>}
            {e.linked_image?.output_url && (
              <img src={e.linked_image.output_url} alt="event" className="img-fluid" />
            )}
            {e.linked_video?.video_url && (
              <video src={e.linked_video.video_url} className="img-fluid" controls />
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function StoryboardEditorPage() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    apiFetch("/storyboard/")
      .then((data) => setEvents(data))
      .catch((err) => console.error("Failed to fetch events", err));
  }, []);

  const handleSave = async (data) => {
    try {
      const res = await apiFetch("/storyboard/", {
        method: "POST",
        body: data,
      });
      setEvents((prev) => [...prev, res]);
    } catch (err) {
      console.error("Failed to save event", err);
    }
  };

  return (
    <div className="container my-5">
      <h1 className="mb-4">🎞️ Storyboard Editor</h1>
      <NarrativeEventEditor onSave={handleSave} />
      <NarrativeTimeline events={events} />
    </div>
  );
}
