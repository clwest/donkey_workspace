import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import { getAccessToken } from "@/utils/auth";
import OnboardingProgressPanel from "@/components/onboarding/OnboardingProgressPanel";

export default function WelcomeBackPage() {
  const navigate = useNavigate();
  const [assistants, setAssistants] = useState([]);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;
    apiFetch("/assistants/").then(setAssistants).catch(() => {});
    apiFetch("/user/", { allowUnauthenticated: true })
      .then(setStatus)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!status) return;
    if (status.assistant_count === 0 && status.onboarding_complete) {
      navigate("/assistants/create", { replace: true });
    } else if (status.assistant_count === 0) {
      navigate("/assistants/launch", { replace: true });
    }
  }, [status, navigate]);

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
      <div className="mt-3">
        <Link to="/assistants/create" className="btn btn-success">
          Create Your First Assistant
        </Link>
      </div>
    </div>
  );
}
