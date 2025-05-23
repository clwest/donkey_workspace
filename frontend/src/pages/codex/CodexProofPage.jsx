import OntologyAuditPanel from "../../components/swarm/OntologyAuditPanel";
import ParadoxDashboard from "../../components/swarm/ParadoxDashboard";

export default function CodexProofPage() {
  return (
    <div className="container my-5">
      <h1 className="mb-3">Codex Integrity Proof</h1>
      <OntologyAuditPanel />
      <ParadoxDashboard />
    </div>
  );
}
