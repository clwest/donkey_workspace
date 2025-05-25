// pages/MythosLandingPage.jsx

import { Link } from "react-router-dom";

export default function MythosLandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-zinc-900 to-black text-white px-6 py-16 flex flex-col items-center justify-center space-y-10 backdrop-blur-md">
      <h1 className="text-7xl font-extrabold tracking-tight text-center drop-shadow-xl">
        🌌 Welcome to MythOS
      </h1>
      <p className="text-xl text-zinc-200 text-center max-w-2xl font-medium drop-shadow-md">
        A symbolic operating system for reflective agents, swarm intelligence, and narrative synchronization.
      </p>
      <p className="text-center text-zinc-400 text-sm">
        Brought to you by Donkey Betz 🧠🥃
      </p>

      <div className="mt-12 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 text-center">
        <Link to="/assistants/primary/interface" className="btn btn-outline-primary shadow-lg">
          🧠 Enter Assistant Interface
        </Link>
        <Link to="/codex" className="btn btn-outline-info shadow-md">
          📜 Explore the Codex
        </Link>
        <Link to="/ritual" className="btn btn-outline-warning shadow-md">
          🧂 Ritual Dashboard
        </Link>
        <Link to="/timeline/memory" className="btn btn-outline-secondary shadow-md">
          ⏳ Memory Timeline
        </Link>
        <Link to="/project/composer" className="btn btn-outline-success shadow-md">
          🛠 Project Composer
        </Link>
      </div>
    </div>
  );
}