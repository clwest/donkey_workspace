import ExecutionChainPlanner from "../../components/plan/ExecutionChainPlanner";

export default function ExecutionChainPage() {
  return (
    <div className="container my-5">
      <h1 className="mb-3">Assistant Execution Chains</h1>
      <ExecutionChainPlanner />
    </div>
  );
}
