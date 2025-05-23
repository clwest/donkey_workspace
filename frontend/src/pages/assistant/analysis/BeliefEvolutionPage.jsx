import { useParams } from "react-router-dom";
import BeliefEvolutionDashboard from "../../../components/assistant/analysis/BeliefEvolutionDashboard";

export default function BeliefEvolutionPage() {
  const { slug } = useParams();
  return (
    <div className="container my-5">
      <h2 className="mb-4">Belief Evolution for {slug}</h2>
      <BeliefEvolutionDashboard assistantId={slug} />
    </div>
  );
}
