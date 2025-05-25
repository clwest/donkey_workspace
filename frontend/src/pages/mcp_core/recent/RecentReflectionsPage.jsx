// frontend/pages/mcp_core/reflections/RecentReflectionsPage.jsx

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import ReflectionMoodChart from "../../../components/mcp_core/ReflectionMoodChart";
import ReflectionMoodFilterBar from "../../../components/mcp_core/ReflectionMoodFilterBar";

export default function RecentReflectionsPage() {
  const [reflections, setReflections] = useState([]);
  const [selectedMood, setSelectedMood] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch(`/mcp/reflections/recent/`).then((data) => {
      setReflections(data);
      setLoading(false);
    });
  }, []);

  const uniqueMoods = [...new Set(reflections.map(r => r.mood || "Unknown"))];

  const filteredReflections = selectedMood
    ? reflections.filter(r => r.mood === selectedMood)
    : reflections;

  if (loading) return <div className="container mt-5">Loading recent reflections...</div>;

  return (
    <div className="container mt-5">
      <h1 className="mb-4">🧠 Recent Reflections (Last 5)</h1>

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
          {filteredReflections.map(reflection => (
            <Link 
              key={reflection.id} 
              to={`/reflections/${reflection.id}`} 
              className="list-group-item list-group-item-action"
            >
              <div className="d-flex w-100 justify-content-between">
                <h5 className="mb-1">{reflection.title || `Reflection #${reflection.id}`}</h5>
                <small>{reflection.created_at}</small>
              </div>
              <p className="mb-1">{reflection.summary.slice(0, 200)}...</p>

              {reflection.tags && reflection.tags.length > 0 && (
                <div className="mt-2">
                  {reflection.tags.map(tag => (
                    <span key={tag} className="badge bg-secondary me-1">{tag}</span>
                  ))}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}