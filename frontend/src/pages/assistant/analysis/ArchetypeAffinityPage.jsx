import { useParams } from "react-router-dom";
import ArchetypeAffinityHeatmap from "../../../components/assistant/analysis/ArchetypeAffinityHeatmap";

export default function ArchetypeAffinityPage() {
  const { slug } = useParams();
  return (
    <div className="container my-5">
      <h2 className="mb-4">Archetype Affinity for {slug}</h2>
      <ArchetypeAffinityHeatmap assistantId={slug} />
    </div>
  );
}
