import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import apiFetch from "../utils/apiClient";
import "./styles/Sidebar.css";

export default function Sidebar({ collapsed }) {
  const [assistants, setAssistants] = useState([]);
  const [memoryOpen, setMemoryOpen] = useState(false);

  useEffect(() => {
    apiFetch("/assistants/")
      .then(setAssistants)
      .catch((err) => console.error("Failed to load assistants", err));
  }, []);

  const primary = assistants.find((a) => a.is_primary);
  const others = assistants.filter((a) => !a.is_primary);

  return (
    <div className={`sidebar bg-light border-end${collapsed ? " collapsed" : ""}`}>
      <div className="p-3">
        <Link to="/" className="navbar-brand mb-3 d-block">
          <span role="img" aria-label="Home">🏠</span>
          <span className="link-text ms-1">Donkey</span>
        </Link>
        <div className="mb-2 fw-bold">My Assistants</div>
        <ul className="list-unstyled mb-3">
          {primary && (
            <li key={primary.id}>
              <NavLink to={`/assistants/${primary.slug}`} className="d-block">
                <span role="img" aria-label="Primary">⭐</span>
                <span className="link-text ms-1">{primary.name}</span>
              </NavLink>
            </li>
          )}
          {others.map((a) => (
            <li key={a.id}>
              <NavLink to={`/assistants/${a.slug}`} className="d-block">
                <span className="link-text">{a.name}</span>
              </NavLink>
            </li>
          ))}
        </ul>
        <div className="mb-2 fw-bold">Library</div>
        <ul className="list-unstyled mb-3">
          <li>
            <NavLink to="/intel/documents" className="d-block">
              <span role="img" aria-label="Documents">📚</span>
              <span className="link-text ms-1">Documents</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/prompts" className="d-block">
              <span role="img" aria-label="Prompts">📄</span>
              <span className="link-text ms-1">Prompts</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/activity" className="d-block">
              <span role="img" aria-label="Activity">📈</span>
              <span className="link-text ms-1">Activity</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/dashboard/world" className="d-block">
              <span role="img" aria-label="World">🌍</span>
              <span className="link-text ms-1">World Dashboard</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/codex" className="d-block">
              <span role="img" aria-label="Codex">📜</span>
              <span className="link-text ms-1">Codex</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/ritual" className="d-block">
              <span role="img" aria-label="Rituals">🔮</span>
              <span className="link-text ms-1">Rituals</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/dev/route-health" className="d-block">
              <span role="img" aria-label="Route">🛣</span>
              <span className="link-text ms-1">Route Health</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/dev/route-explorer" className="d-block">
              <span role="img" aria-label="Explorer">🗺</span>
              <span className="link-text ms-1">Route Explorer</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/dev/auth-debug" className="d-block">
              <span role="img" aria-label="Auth">🔑</span>
              <span className="link-text ms-1">Auth Debug</span>
            </NavLink>
          </li>
        </ul>
        <div className="mb-2 fw-bold d-flex align-items-center">
          <span className="flex-grow-1">Memory</span>
          <button
            className="btn btn-sm btn-link"
            onClick={() => setMemoryOpen(!memoryOpen)}
          >
            {memoryOpen ? "▼" : "▶"}
          </button>
        </div>
        {memoryOpen && (
          <ul className="list-unstyled mb-3">
            <li>
              <NavLink to="/memories" className="d-block">
                🧠 Browser
              </NavLink>
            </li>
            <li>
              <NavLink to="/memories/reflect" className="d-block">
                ✨ Reflect
              </NavLink>
            </li>
            <li>
              <NavLink to="/memory/predict" className="d-block">
                🔮 Predict
              </NavLink>
            </li>
            <li>
              <NavLink to="/memory/synthesize" className="d-block">
                🧬 Synthesize
              </NavLink>
            </li>
            <li>
              <NavLink to="/timeline/memory" className="d-block">
                📅 Timeline
              </NavLink>
            </li>
          </ul>
        )}
      </div>
    </div>
  );
}
