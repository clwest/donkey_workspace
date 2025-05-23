import { useParams } from "react-router-dom";
import VisualArchetypeCard from "../../components/swarm/VisualArchetypeCard";

export default function MythOSAssistantPage() {
  const { id } = useParams();
  return (
    <div className="container my-5">
      <h1>Assistant Archetype</h1>
      <VisualArchetypeCard assistantId={id} />
    </div>
  );
}
