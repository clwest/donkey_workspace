import BeliefContinuityDashboard from "../../components/swarm/BeliefContinuityDashboard";
import ContinuityAnchorCard from "../../components/assistant/memory/ContinuityAnchorCard";

export default function ContinuityAnchorPage() {
  return (
    <div className="container my-5">
      <h1 className="mb-3">Continuity Anchor</h1>
      <BeliefContinuityDashboard />
      <ContinuityAnchorCard />
    </div>
  );
}
