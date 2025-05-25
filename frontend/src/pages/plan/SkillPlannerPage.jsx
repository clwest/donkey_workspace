import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

export default function SkillPlannerPage() {
  const { id } = useParams();
  const [plan, setPlan] = useState(null);

  useEffect(() => {
    if (!id) return;
    apiFetch(`/plan/skills/${id}/`)
      .then(setPlan)
      .catch((err) => console.error("Failed to load skill planner", err));
  }, [id]);

  return (
    <div className="container my-4">
      <h3>Skill Planner</h3>
      <pre>{JSON.stringify(plan, null, 2)}</pre>
    </div>
  );
}
