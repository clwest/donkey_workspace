// frontend/components/Navbar.jsx

import { Link, NavLink } from "react-router-dom";
import { useEffect, useState } from "react";
import "./styles/Navbar.css";
import FeedbackWidget from "./feedback/FeedbackWidget";
import LanguageSelector from "./LanguageSelector";
import HighContrastToggle from "./HighContrastToggle";
import apiFetch from "../utils/apiClient";

export default function Navbar({ onToggleSidebar }) {
  const [orphanCount, setOrphanCount] = useState(0);

  useEffect(() => {
    async function fetchAudit() {
      try {
        const res = await apiFetch("/dev/embedding-audit/");
        const count = res.results.reduce((acc, [_, r]) => acc + r.orphans, 0);
        setOrphanCount(count);
      } catch (err) {
        // ignore
      }
    }
    fetchAudit();
  }, []);
  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light mb-4">
      <div className="container-fluid">
        <Link className="navbar-brand me-2" to="/">
          🌠 MythOS
        </Link>
        <button
          className="btn btn-outline-secondary btn-sm me-2"
          type="button"
          onClick={onToggleSidebar}
        >
          ☰
        </button>

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
              <Link className="nav-link" to="/memories/bookmarked">
                ⭐️ Bookmarked
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
                  <Link className="dropdown-item" to="/assistants/onboarding">
                    ✨ Onboarding
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item start-tour-link" to="/tour">
                    🗺 Start Tour
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/assistants/create">
                    ➕ Create Assistant
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/badges">
                    🏷️ Badges
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
                  <Link className="dropdown-item" to="/assistants/primary/objectives">
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
                <li>
                  <Link className="dropdown-item" to="/anchor/mutations">
                    🔀 Glossary Mutations
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/anchor/diagnostics">
                    🧩 Anchor Diagnostics
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/keeper/logs">
                    📜 Keeper Logs
                  </Link>
                </li>
              </ul>
            </li>
            <li className="nav-item dropdown">
              <button
                className="nav-link dropdown-toggle btn btn-link"
                data-bs-toggle="dropdown"
              >
                🎨 Media
              </button>
              <ul className="dropdown-menu">
                <li>
                  <Link className="dropdown-item" to="/images">
                    🖼 Gallery
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/images/new">
                    ➕ Create Image
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/characters">
                    🎭 Characters
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/stories">
                    📚 Stories
                  </Link>
                </li>
              </ul>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/dev-dashboard">
                🛠 Dev Dashboard
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/tools">
                🔧 Tools
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/tools/index">
                🗂 Tool Index
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/dev/route-health">
                🛣 Route Health
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/dev/route-explorer">
                🗺 Route Explorer
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/dev/auth-debug">
                🔑 Auth Debug
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/devtools/embedding-debug">
                🧩 Embedding Debug
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/devtools/embedding-audit">
                🩺 Embedding Audit
                {orphanCount > 0 && (
                  <span className="badge bg-danger ms-1">{orphanCount}</span>
                )}
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/devtools/drift-log">
                📈 Drift Log
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/dev/onboarding-debug">
                🧭 Onboarding Debug
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/project/composer">
                🛠️ Project Composer
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/debug/prompts">
                🔍 Prompt Debugger
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/dev/cli">
                🖥 CLI Runner
              </Link>
            </li>
            <li className="nav-item dropdown">
              <button
                className="nav-link dropdown-toggle btn btn-link"
                data-bs-toggle="dropdown"
              >
                📜 Codex
              </button>
              <ul className="dropdown-menu">
                <li>
                  <Link className="dropdown-item" to="/codex">
                    📚 Codex Home
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/codex/stabilize">
                    🛠 Stabilization
                  </Link>
                </li>
              </ul>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/evolve/swarm">
                🧪 Swarm Evolution
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
            <Link className="btn btn-outline-primary btn-sm me-2" to="/home">
              🏠 Home
            </Link>
            <Link className="btn btn-outline-secondary btn-sm me-2" to="/login">
              Login
            </Link>
            <Link className="btn btn-outline-secondary btn-sm me-2" to="/register">
              Register
            </Link>
            <Link className="btn btn-outline-secondary btn-sm me-2" to="/profile">
              Profile
            </Link>
            <LanguageSelector />
            <HighContrastToggle />
            <FeedbackWidget />
            <Link className="btn btn-outline-secondary btn-sm" to="/logout">
              Logout
            </Link>
          </span>
        </div>
      </div>
    </nav>
  );
}
