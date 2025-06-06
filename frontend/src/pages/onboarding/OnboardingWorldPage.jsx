import { useNavigate } from "react-router-dom";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import useOnboardingGuard, { STEP_ROUTES } from "../../onboarding/useOnboardingGuard";
import useOnboardingTracker from "@/hooks/useOnboardingTracker";
import { ONBOARDING_WORLD } from "../../onboarding/metadata";

export default function OnboardingWorldPage() {
  useOnboardingGuard("world");
  const { progress, nextStep, percent } = useOnboardingTracker();
  const navigate = useNavigate();

  const getStatus = (slug) => progress?.find((p) => p.step === slug)?.status || "pending";

  return (
    <div className="container my-4">
      <OnboardingProgressBar />
      <OnboardingProgressPanel />
      <h2>{ONBOARDING_WORLD.title}</h2>
      <div className="d-flex flex-wrap gap-3">
        {ONBOARDING_WORLD.nodes.map((node) => {
          const status = getStatus(node.slug);
          const highlight = nextStep === node.slug;
          const handleClick = () => {
            if (status !== "completed" && node.slug !== nextStep) {
              alert(node.description);
              return;
            }
            navigate(STEP_ROUTES[node.slug]);
          };
          return (
            <div
              key={node.slug}
              className={`card node-card ${highlight ? "pulse border-primary" : ""}`}
              onClick={handleClick}
              title={node.description}
              style={{ cursor: "pointer", width: "160px" }}
            >
              <h5 className="mb-1">{node.title}</h5>
              <small className="text-muted">{status}</small>
            </div>
          );
        })}
      </div>
    </div>
  );
}
