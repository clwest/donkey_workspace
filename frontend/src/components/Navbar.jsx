// frontend/components/Navbar.jsx

import { Link, NavLink } from "react-router-dom";
import "./styles/Navbar.css";

export default function Navbar() {
  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light mb-4">
      <div className="container-fluid">
        <Link className="navbar-brand" to="/">
          🏠 Donkey Assistant
        </Link>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarContent"
          aria-controls="navbarContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon " />
        </button>

        <div className="collapse navbar-collapse" id="navbarContent">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            {/* Core Sections */}
            <li className="nav-item">
              <Link className="nav-link" to="/prompts">
                📄 Prompts
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/memories">
                🧠 Memories
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/memories/chains">
                🔗 Memory Chains
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/reflections/custom">
                🛠 Custom Reflection
              </Link>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/assistants/primary">
                🌐 Orchestrator
              </NavLink>
            </li>

            {/* Assistant Project Dashboard */}
            <li className="nav-item"></li>

            {/* Assistant Modules */}
            <li className="nav-item dropdown">
              <button
                className="nav-link dropdown-toggle btn btn-link"
                data-bs-toggle="dropdown"
              >
                🤖 Assistant
              </button>
              <ul className="dropdown-menu">
                <li>
                  <Link className="dropdown-item" to="/assistant-dashboard">
                    🚀 Dashboard
                  </Link>
                </li>

                <li>
                  <Link className="dropdown-item" to="/prompts/assistant">
                    🧪 Prompt Creation Assistant
                  </Link>
                </li>
                <li>
                  <hr className="dropdown-divider" />
                </li>
                <li>
                  <Link className="dropdown-item" to="/assistants">
                    🧑‍💻 All Assistants
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/assistants/create">
                    ➕ Create Assistant
                  </Link>
                </li>
                <li>
                  <hr className="dropdown-divider" />
                </li>
                <li>
                  <Link
                    className="dropdown-item"
                    to="/assistants/memory-chains"
                  >
                    🔗 Memory Chains
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/assistants/reflections">
                    🪞 Reflections
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/assistants/objectives">
                    🎯 Objectives
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/assistants/next-actions">
                    📋 Next Actions
                  </Link>
                </li>
                <li>
                  <hr className="dropdown-divider" />
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/assistants-demos">
                    🧪 Assistant Demos
                  </Link>
                  <Link className="nav-link" to="/assistants/projects">
                    🗂 Assistant Projects
                  </Link>
                </li>
              </ul>
            </li>

            <li className="nav-item dropdown">
              <button
                className="nav-link dropdown-toggle btn btn-link"
                data-bs-toggle="dropdown"
              >
                📚 Intel
              </button>

              <ul className="dropdown-menu">
                <li>
                  <Link className="dropdown-item" to="/intel/documents">
                    📄 Document Browser
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/intel/load-url">
                    🌐 Load URL
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/intel/load-pdf">
                    📎 Upload PDFs
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/intel/jobs">
                    ⏳ Job Status
                  </Link>
                </li>
              </ul>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/dev-dashboard">
                🛠 Dev Dashboard
              </Link>
            </li>

            {/* Signal Intelligence */}
            <li className="nav-item dropdown">
              <button
                className="nav-link dropdown-toggle btn btn-link"
                data-bs-toggle="dropdown"
              >
                📡 Signals
              </button>
              <ul className="dropdown-menu">
                <li>
                  <Link className="dropdown-item" to="/assistants/sources">
                    🌐 Sources
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/assistants/signals">
                    ⚡ Catches
                  </Link>
                </li>
              </ul>
            </li>

            {/* Reflection Quick Actions */}
            <li className="nav-item dropdown">
              <button
                className="nav-link dropdown-toggle btn btn-link"
                data-bs-toggle="dropdown"
              >
                🪞 Reflections
              </button>
              <ul className="dropdown-menu">
                <li>
                  <Link className="dropdown-item" to="/reflect">
                    Reflect Now
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/reflections">
                    History
                  </Link>
                </li>
              </ul>
            </li>
          </ul>

          {/* Right-aligned Links */}
          <span className="navbar-text">
            <Link className="btn btn-outline-primary btn-sm" to="/">
              🏠 Home
            </Link>
          </span>
        </div>
      </div>
    </nav>
  );
}
