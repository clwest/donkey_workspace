import useOnboardingTracker from "@/hooks/useOnboardingTracker";
import { Link } from "react-router-dom";

export default function WelcomePage() {
  const { progress } = useOnboardingTracker();
  const steps = [
    "Name your assistant",
    "Choose an archetype",
    "Begin onboarding world",
  ];
  return (
    <div className="container my-5">
      <div className="card shadow">
        <div className="card-body text-center">
          <h2 className="card-title mb-3">You’re in! Let’s build your first assistant.</h2>
          <ul className="list-unstyled mb-4">
            {steps.map((s) => (
              <li key={s}>✅ {s}</li>
            ))}
          </ul>
          <Link to="/onboarding" className="btn btn-primary">
            Start Onboarding
          </Link>
        </div>
      </div>
      {progress && (
        <div className="mt-4">
          <h5>Current Progress</h5>
          <ul className="list-unstyled">
            {progress.map((p) => (
              <li key={p.step}>
                {p.status === "completed" ? "✅" : "⬜"} {p.step}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
