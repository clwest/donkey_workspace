import { Link } from "react-router-dom";

export default function UserMythpathInitializer() {
  return (
    <div className="container my-4">
      <h2>Choose Your Mythpath</h2>
      <ul>
        <li>
          <Link to="/onboarding/world?path=memory">Memory Seeker</Link>
          <div className="text-muted small">Reflective tone, memory tag</div>
        </li>
        <li>
          <Link to="/onboarding/world?path=codex">Codex Explorer</Link>
          <div className="text-muted small">Precise tone, codex tag</div>
        </li>
        <li>
          <Link to="/onboarding/world?path=ritual">Ritual Witness</Link>
          <div className="text-muted small">Observant tone, ritual tag</div>
        </li>
      </ul>
    </div>
  );
}
