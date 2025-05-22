import { useEffect, useState } from "react";
import { fetchMythflowInsights } from "../../api/agents";

export default function MythflowInsightFeed() {
  const [insights, setInsights] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchMythflowInsights();
        setInsights(data.results || data);
      } catch (err) {
        console.error("Failed to load insights", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Mythflow Insights</h5>
      <ul className="list-group">
        {insights.map((i) => (
          <li key={i.id} className="list-group-item">
            {i.insight_summary}
          </li>
        ))}
        {insights.length === 0 && (
          <li className="list-group-item text-muted">No insights.</li>
        )}
      </ul>
    </div>
  );
}
