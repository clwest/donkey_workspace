import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import apiFetch from "../utils/apiClient";
import "./styles/Sidebar.css";

export default function Sidebar() {
  const [assistants, setAssistants] = useState([]);

  useEffect(() => {
    apiFetch("/assistants/")
      .then(setAssistants)
      .catch((err) => console.error("Failed to load assistants", err));
  }, []);

  const primary = assistants.find((a) => a.is_primary);
  const others = assistants.filter((a) => !a.is_primary);

  return (
    <div className="sidebar bg-light border-end">
      <div className="p-3">
        <Link to="/" className="navbar-brand mb-3 d-block">
          🏠 Donkey
        </Link>
        <div className="mb-2 fw-bold">My Assistants</div>
        <ul className="list-unstyled mb-3">
          {primary && (
            <li key={primary.id}>
              <NavLink to={`/assistants/${primary.slug}`} className="d-block">
                ⭐ {primary.name}
              </NavLink>
            </li>
          )}
          {others.map((a) => (
            <li key={a.id}>
              <NavLink to={`/assistants/${a.slug}`} className="d-block">
                {a.name}
              </NavLink>
            </li>
          ))}
        </ul>
        <div className="mb-2 fw-bold">Library</div>
        <ul className="list-unstyled mb-3">
          <li>
            <NavLink to="/intel/documents" className="d-block">
              📚 Documents
            </NavLink>
          </li>
          <li>
            <NavLink to="/prompts" className="d-block">
              📄 Prompts
            </NavLink>
          </li>
          <li>
            <NavLink to="/activity" className="d-block">
              📈 Activity
            </NavLink>
          </li>
          <li>
            <NavLink to="/dashboard/world" className="d-block">
              🌍 World Dashboard
            </NavLink>
          </li>
          <li>
            <NavLink to="/codex" className="d-block">
              📜 Codex
            </NavLink>
          </li>
          <li>
            <NavLink to="/ritual" className="d-block">
              🔮 Rituals
            </NavLink>
          </li>
          <li>
            <NavLink to="/dev/routes" className="d-block">
              🛣 Route Health
            </NavLink>
          </li>
        </ul>
      </div>
    </div>
  );
}
