import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import SkillGraphPanel from "../../../components/assistant/skills/SkillGraphPanel";

export default function SkillGraphPage() {
  const { slug } = useParams();
  const [assistant, setAssistant] = useState(null);

  useEffect(() => {
    async function fetchData() {
      const data = await apiFetch(`/assistants/${slug}/`);
      setAssistant(data);
    }
    fetchData();
  }, [slug]);

  if (!assistant) return <div className="container my-4">Loading...</div>;
  return (
    <div className="container my-4">
      <h3>{assistant.name} Skill Graph</h3>
      <SkillGraphPanel assistant={assistant} />
    </div>
  );
}
