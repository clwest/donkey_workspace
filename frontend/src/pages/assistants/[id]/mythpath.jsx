import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "@/utils/apiClient";

export default function AssistantMythpathPage() {
  const { id } = useParams();
  const [events, setEvents] = useState([]);

  useEffect(() => {
    apiFetch(`/assistants/${id}/mythpath/`).then((res) => {
      setEvents(res.events || []);
    });
  }, [id]);

  return (
    <div className="container my-4">
      <h1 className="mb-3">Mythpath Timeline</h1>
      <ul>
        {events.map((e, idx) => (
          <li key={idx}>{e.event_type} – {e.description}</li>
        ))}
      </ul>
    </div>
  );
}
