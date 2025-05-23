import CodexTrendSurfaceVisualizer from "../../components/CodexTrendSurfaceVisualizer";
import CodexMutationViewer from "../../components/CodexMutationViewer";

export default function CodexConvergePage() {
  return (
    <div className="container my-5">
      <h1 className="mb-3">Codex Convergence</h1>
      <CodexTrendSurfaceVisualizer />
      <div className="mt-3">
        <CodexMutationViewer />
      </div>
    </div>
  );
}
