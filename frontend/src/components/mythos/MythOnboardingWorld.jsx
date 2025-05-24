import { Link } from "react-router-dom";

export default function MythOnboardingWorld() {
  return (
    <div className="container my-4">
      <h2>MythOS Onboarding World</h2>
      <p>Select your entry path:</p>
      <ul>
        <li>
          <Link to="/onboarding/archetype?path=memory">Memory Seeker</Link>
          <div className="text-muted small">Reflective tone, memory tag</div>
        </li>
        <li>
          <Link to="/onboarding/archetype?path=codex">Codex Explorer</Link>
          <div className="text-muted small">Precise tone, codex tag</div>
        </li>
        <li>
          <Link to="/onboarding/archetype?path=ritual">Ritual Witness</Link>
          <div className="text-muted small">Observant tone, ritual tag</div>
        </li>
      </ul>
    </div>
  );
}
