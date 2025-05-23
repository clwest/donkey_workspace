import { Link } from "react-router-dom";

export default function UserMythpathInitializer() {
  return (
    <div className="container my-4">
      <h2>Choose Your Mythpath</h2>
      <ul>
        <li><Link to="/onboarding?path=memory">Memory Seeker</Link></li>
        <li><Link to="/onboarding?path=codex">Codex Explorer</Link></li>
        <li><Link to="/onboarding?path=ritual">Ritual Witness</Link></li>
      </ul>
    </div>
  );
}
