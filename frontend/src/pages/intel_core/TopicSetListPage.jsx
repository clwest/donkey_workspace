import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function TopicSetListPage() {
  const [topicSets, setTopicSets] = useState([]);

  useEffect(() => {
    apiFetch("/intel/topic-sets/")
      .then((d) => setTopicSets(d || []))
      .catch(() => setTopicSets([]));
  }, []);

  return (
    <div className="container py-4">
      <h2>📑 Topic Sets</h2>
      <ul className="list-group">
        {topicSets.map((ts) => (
          <li key={ts.id} className="list-group-item">
            <strong>{ts.title}</strong>
            <div className="small text-muted">{ts.description}</div>
            <div className="small text-muted">
              Anchor: {ts.auto_suggested_anchor || "-"}
            </div>
            <div className="small text-muted">
              Chunks: {ts.related_chunks?.length || 0}
            </div>
          </li>
        ))}
        {topicSets.length === 0 && (
          <li className="list-group-item text-muted">No topic sets found.</li>
        )}
      </ul>
    </div>
  );
}
