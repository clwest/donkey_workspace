import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";
import useOnboardingTracker from "@/hooks/useOnboardingTracker";
import apiFetch from "@/utils/apiClient";
import AssistantSetupSummary from "../../components/assistant/AssistantSetupSummary";
import GuideChatPanel from "../../components/onboarding/GuideChatPanel";
import OnboardingHelpButton from "../../components/onboarding/OnboardingHelpButton";

export default function OnboardingWizardPage() {
  const [step, setStep] = useState(1);
  const total = 6;
  const navigate = useNavigate();

  useOnboardingGuard("wizard");
  useOnboardingTracker();
  const [primary, setPrimary] = useState(null);

  useEffect(() => {
    if (step !== total) return;
    apiFetch("/assistants/primary/")
      .then(setPrimary)
      .catch(() => {});
  }, [step]);


  const next = () => setStep((s) => Math.min(s + 1, total));
  const back = () => setStep((s) => Math.max(s - 1, 1));

  const finish = () => {
    navigate("/");
  };

  return (
    <div className="container my-5">
      <GuideChatPanel />
      <OnboardingProgressBar />
      <OnboardingProgressPanel />
      <h2>Onboarding Wizard</h2>
      <div className="mb-3">Step {step} of {total}</div>
      {step === 1 && (
        <div>
          <h4>Welcome!</h4>
          <p>Hey there, let&rsquo;s get you set up.</p>
        </div>
      )}
      {step === 2 && (
        <div>
          <h4>Create Your Master Assistant</h4>
          <div className="mb-2">
            <label className="form-label">Name</label>
            <input className="form-control" placeholder="Assistant name" />
          </div>
          <div className="mb-2">
            <label className="form-label">One-liner bio</label>
            <input className="form-control" placeholder="Curious collaborator" />
          </div>
        </div>
      )}
      {step === 3 && (
        <div>
          <h4>Personal Profile</h4>
          <div className="mb-2">
            <label className="form-label">Main goals</label>
            <input className="form-control" placeholder="e.g. Learn more" />
          </div>
          <div className="mb-2">
            <label className="form-label">Interests</label>
            <input className="form-control" placeholder="e.g. chess, BBQ" />
          </div>
        </div>
      )}
      {step === 4 && (
        <div>
          <h4>Import Knowledge Base</h4>
          <button className="btn btn-outline-secondary me-2">Upload PDF</button>
          <button className="btn btn-outline-secondary me-2">Paste YouTube URL</button>
          <button className="btn btn-outline-secondary">Add Website URL</button>
        </div>
      )}
      {step === 5 && (
        <div>
          <h4>Quick Tour</h4>
          <p>Check the sidebar for your assistants and docs library.</p>
        </div>
      )}
      {step === 6 && (
        <div>
          <h4>Finish &amp; Go!</h4>
          <p>You&apos;re all set—have at it!</p>
          {primary && (
            <div className="my-3">
              <AssistantSetupSummary assistant={primary} />
            </div>
          )}
        </div>
      )}
      <div className="mt-4">
        {step > 1 && (
          <button className="btn btn-secondary me-2" onClick={back}>
            Back
          </button>
        )}
        {step < total && (
          <button className="btn btn-primary" onClick={next}>
            Next
          </button>
        )}
        {step === total && (
          <button className="btn btn-success" onClick={finish}>
            Finish
          </button>
        )}
      </div>
      <OnboardingHelpButton />
    </div>
  );
}
