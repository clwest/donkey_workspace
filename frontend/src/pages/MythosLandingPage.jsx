import React from "react";
import { Link } from "react-router-dom";

export default function MythOSLandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-zinc-900 to-black text-white p-10 flex flex-col items-center justify-center space-y-6">
      <h1 className="text-5xl font-bold tracking-tight text-center">
        🌌 Welcome to MythOS
      </h1>
      <p className="text-lg text-zinc-400 text-center max-w-xl">
        A symbolic operating system for reflective agents, swarm intelligence, and narrative synchronization.
      </p>
      <div className="text-center text-zinc-500 italic">Brought to you by <span className="text-white font-semibold">Donkey Betz</span> 🧠📜</div>
      <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-6">
        <Link
          to="/assistants"
          className="bg-zinc-800 hover:bg-zinc-700 px-6 py-3 rounded-xl shadow-xl text-center"
        >
          🧠 Enter Assistant Interface
        </Link>
        <Link
          to="/codex"
          className="bg-zinc-800 hover:bg-zinc-700 px-6 py-3 rounded-xl shadow-xl text-center"
        >
          📜 Explore the Codex
        </Link>
        <Link
          to="/ritual"
          className="bg-zinc-800 hover:bg-zinc-700 px-6 py-3 rounded-xl shadow-xl text-center"
        >
          🔁 Ritual Dashboard
        </Link>
        <Link
          to="/timeline"
          className="bg-zinc-800 hover:bg-zinc-700 px-6 py-3 rounded-xl shadow-xl text-center"
        >
          ⏳ Memory Timeline
        </Link>
      </div>
    </div>
  );
}
