import RoleAdaptiveTaskAssignmentEngine from "../../components/swarm/RoleAdaptiveTaskAssignmentEngine";

export default function TaskAssignmentPage() {
  return (
    <div className="container my-5">
      <h1 className="mb-3">Role-Adaptive Task Assignment</h1>
      <RoleAdaptiveTaskAssignmentEngine />
    </div>
  );
}
