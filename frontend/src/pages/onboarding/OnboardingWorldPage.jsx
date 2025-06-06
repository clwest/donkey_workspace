import { useNavigate } from "react-router-dom";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import OnboardingIntroModal from "../../components/onboarding/OnboardingIntroModal";
import useOnboardingGuard, { STEP_ROUTES } from "../../onboarding/useOnboardingGuard";
import useOnboardingTracker from "@/hooks/useOnboardingTracker";
import useUserInfo from "@/hooks/useUserInfo";
import { ONBOARDING_WORLD } from "../../onboarding/metadata";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Tooltip from "react-bootstrap/Tooltip";

export default function OnboardingWorldPage() {

  useOnboardingGuard("world");
  const { progress, nextStep } = useOnboardingTracker();

  const userInfo = useUserInfo();

  const navigate = useNavigate();

  if (!progress || !userInfo) return <div className="container my-5">Loading...</div>;

  const getStatus = (slug) => progress?.find((p) => p.step === slug)?.status || "pending";

  return (
    <div className="container my-4">
      <OnboardingIntroModal />
      <OnboardingProgressBar />
      <OnboardingProgressPanel />
      <h2>{ONBOARDING_WORLD.title}</h2>
      <div className="d-flex flex-wrap gap-3">
        {ONBOARDING_WORLD.nodes.map((node) => {
          const status = getStatus(node.slug);
          const highlight = nextStep === node.slug;
          const handleClick = () => {
            if (status !== "completed" && node.slug !== nextStep) {
              return;
            }
            navigate(STEP_ROUTES[node.slug]);
          };
          return (
            <div key={node.slug} className="position-relative">
              <div
                className={`card node-card ${highlight ? "pulse border-primary" : ""}`}
                onClick={handleClick}
                style={{ cursor: "pointer", width: "160px" }}
              >
                <h5 className="mb-1">
                  {node.emoji} {node.title}
                </h5>
                <small className="text-muted">{status}</small>
              </div>
              <OverlayTrigger
                placement="top"
                overlay={<Tooltip>{node.description}</Tooltip>}
              >
                <span className="position-absolute top-0 end-0 me-1 mt-1 text-muted" style={{ cursor: 'help' }}>?</span>
              </OverlayTrigger>
            </div>
          );
        })}
      </div>
      <div className="mt-4 border-top pt-3">
        <h5>Summary</h5>
        <p>Name: {userInfo.assistant_name || "-"}</p>
        <p>Avatar: {userInfo.avatar_style || "-"}</p>
        <p>Tone: {userInfo.tone_profile || "-"}</p>
        <p>Glossary taught: {userInfo.glossary_score || 0}</p>
        {userInfo.initial_badges?.length > 0 && (
          <p>Badge unlocked: {userInfo.initial_badges[0]}</p>
        )}
        <button className="btn btn-success" onClick={() => navigate("/home")}>Launch Your Assistant!</button>
      </div>
    </div>
  );
}
