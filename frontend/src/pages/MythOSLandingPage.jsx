import { Link } from "react-router-dom";

export default function MythOSLandingPage() {
  return (
    <div className="min-h-screen text-white bg-gradient-to-br from-black via-zinc-900 to-black flex flex-col items-center justify-center py-16 px-6 space-y-12">
      <div className="text-center space-y-4">
        <h1 className="text-6xl font-extrabold tracking-tight drop-shadow-xl">Welcome to MythOS</h1>
        <p className="text-xl text-zinc-300 max-w-2xl mx-auto">
          Your intelligence, extended. Train assistants, reflect on memory, and evolve insight.
        </p>
      </div>
      <div className="flex space-x-4">
        <Link to="/register" className="btn btn-success">Get Started</Link>
        <Link to="/login" className="btn btn-primary">Log In</Link>
        <Link to="/assistants/demo" className="btn btn-secondary">View Demo</Link>
        <a href="#features" className="btn btn-outline-light">Learn More</a>
      </div>
      <div id="features" className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl text-center">
        <div>
          <h3 className="text-2xl font-bold mb-2">🌱 Assistant Glossary Growth</h3>
          <p className="text-zinc-300">Expand your assistant vocabulary with anchored terminology.</p>
        </div>
        <div>
          <h3 className="text-2xl font-bold mb-2">🔁 Memory Reflection Engine</h3>
          <p className="text-zinc-300">Review conversations and reinforce key insights automatically.</p>
        </div>
        <div>
          <h3 className="text-2xl font-bold mb-2">🧠 Multi-Agent Skill Badges</h3>
          <p className="text-zinc-300">Unlock collaborative abilities and visualize strengths.</p>
        </div>
        <div>
          <h3 className="text-2xl font-bold mb-2">🧭 Swarm-Oriented Planning</h3>
          <p className="text-zinc-300">Coordinate teams of assistants toward complex goals.</p>
        </div>
      </div>
      <footer className="mt-16 text-center text-zinc-400 text-sm">
        <p>MythOS — You don’t prompt MythOS. You grow it.</p>
        <p>
          <a href="https://github.com/example" className="underline">
            GitHub
          </a>
        </p>
      </footer>
    </div>
  );
}
