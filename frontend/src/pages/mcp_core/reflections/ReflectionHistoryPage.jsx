import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import ReflectionMoodChart from "../../../components/mcp_core/ReflectionMoodChart";
import ReflectionMoodFilterBar from "../../../components/mcp_core/ReflectionMoodFilterBar";

const moodColors = {
  optimistic: "success",
  positive: "success",
  neutral: "secondary",
  concerned: "warning",
  cautious: "warning",
  anxious: "danger",
  frustrated: "danger",
  thoughtful: "info",
  focused: "primary",
  overwhelmed: "danger",
  energized: "success",
  analytical: "info",  
};

export default function ReflectionHistoryPage() {
  const [reflections, setReflections] = useState([]);
  const [selectedMood, setSelectedMood] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/mcp/reflections/")
      .then((res) => res.json())
      .then((data) => {
        // Handle paginated results from DRF list endpoints
        const items = Array.isArray(data) ? data : data.results || [];
        setReflections(items);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch reflections:", err);
        setLoading(false);
      });
  }, []);

  const uniqueMoods = [...new Set(reflections.map(r => r.mood || "Unknown"))];

  const filteredReflections = selectedMood
    ? reflections.filter(r => r.mood === selectedMood)
    : reflections;

  if (loading) return <div className="container mt-5">Loading reflections...</div>;

  return (
    <div className="container mt-5">
      <h1 className="mb-4">🧠 Reflection History</h1>

      <ReflectionMoodChart reflections={reflections} onMoodSelect={setSelectedMood} />

      <ReflectionMoodFilterBar
        moods={uniqueMoods}
        selectedMood={selectedMood}
        onMoodSelect={setSelectedMood}
      />

      {filteredReflections.length === 0 ? (
        <p>No reflections match the selected mood.</p>
      ) : (
        <div className="list-group">
          {filteredReflections.map(reflection => {
            const mood = reflection.mood || "Unknown";
            const badgeColor = moodColors[mood.toLowerCase()] || "secondary";
            return (
              <Link
                to={`/reflections/${reflection.id}`}
                key={reflection.id}
                className="list-group-item list-group-item-action"
              >
                <div className="d-flex w-100 justify-content-between">
                  <h5 className="mb-1">{reflection.title || `Reflection #${reflection.id}`}</h5>
                  <small className="text-muted">{reflection.created_at}</small>
                </div>
                <p className="mb-1">{reflection.summary.slice(0, 200)}...</p>
                <div>
                  <span className={`badge rounded-pill bg-${badgeColor}`}>
                    {mood.charAt(0).toUpperCase() + mood.slice(1)}
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}