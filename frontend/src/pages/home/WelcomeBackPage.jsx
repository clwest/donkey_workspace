import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import OnboardingProgressPanel from "@/components/onboarding/OnboardingProgressPanel";

export default function WelcomeBackPage() {
  const [assistants, setAssistants] = useState([]);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    apiFetch("/assistants/").then(setAssistants).catch(() => {});
    apiFetch("/user/").then(setStatus).catch(() => {});
  }, []);

  const onboardingIncomplete = status && !status.onboarding_complete;

  return (
    <div className="container my-5">
      <h2 className="mb-3">Welcome Back</h2>
      {onboardingIncomplete && (
        <div className="alert alert-info">
          <p className="mb-2">Finish setting up your first assistant.</p>
          <Link to="/onboarding/world" className="btn btn-primary me-2">
            Continue Onboarding
          </Link>
        </div>
      )}
      {onboardingIncomplete && <OnboardingProgressPanel />}
      <h5>Your Assistants</h5>
      {assistants.length === 0 ? (
        <p>No assistants yet.</p>
      ) : (
        <ul className="list-group">
          {assistants.map((a) => (
            <li key={a.id} className="list-group-item d-flex justify-content-between">
              <span>{a.name}</span>
              <Link to={`/assistants/${a.slug}/`} className="btn btn-sm btn-outline-secondary">
                Open
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
