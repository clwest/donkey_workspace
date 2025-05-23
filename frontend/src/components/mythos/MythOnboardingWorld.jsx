import { Link } from "react-router-dom";

export default function MythOnboardingWorld() {
  return (
    <div className="container my-4">
      <h2>MythOS Onboarding World</h2>
      <p>Select your entry path:</p>
      <ul>
        <li>
          <Link to="/onboarding/archetype?path=memory">Memory Seeker</Link>
        </li>
        <li>
          <Link to="/onboarding/archetype?path=codex">Codex Explorer</Link>
        </li>
        <li>
          <Link to="/onboarding/archetype?path=ritual">Ritual Witness</Link>
        </li>
      </ul>
    </div>
  );
}
