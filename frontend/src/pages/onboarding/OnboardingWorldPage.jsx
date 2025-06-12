import { useNavigate } from "react-router-dom";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import OnboardingIntroModal from "../../components/onboarding/OnboardingIntroModal";
import { useEffect } from "react";
import useOnboardingGuard, { STEP_ROUTES } from "../../onboarding/useOnboardingGuard";
import useOnboardingTracker from "@/hooks/useOnboardingTracker";
import useUserInfo from "@/hooks/useUserInfo";
import OnboardingWrapper from "../../components/onboarding/OnboardingWrapper";
import GuideChatPanel from "../../components/onboarding/GuideChatPanel";
import { ONBOARDING_WORLD } from "../../onboarding/metadata";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Tooltip from "react-bootstrap/Tooltip";
import OnboardingHelpButton from "../../components/onboarding/OnboardingHelpButton";
import useOnboardingTheme from "../../onboarding/useOnboardingTheme";


export default function OnboardingWorldPage() {

  useOnboardingGuard("world");
  const { theme, toggle } = useOnboardingTheme();
  const { progress, nextStep, aliases, onboardingComplete } =
    useOnboardingTracker(theme);

  const userInfo = useUserInfo();
  if (!userInfo) {
    console.warn(
      "User info not loaded — skipping assistant count fallback."
    );
  }
  const count = userInfo?.assistant_count ?? 0;

  const navigate = useNavigate();

  useEffect(() => {
    console.warn("[onboarding] userInfo", userInfo);
    if (!onboardingComplete) return;
    const id = setTimeout(() => {
      if (count > 0) {
        navigate("/home", { replace: true });
      } else {
        navigate("/assistants/create", { replace: true });
      }
    }, 5000);
    return () => clearTimeout(id);
  }, [onboardingComplete, userInfo, navigate]);

  if (!progress || !userInfo) return <div className="container my-5">Loading...</div>;

  const getStatus = (slug) => progress?.find((p) => p.step === slug)?.status || "pending";
  const mythIncomplete = progress.find((p) => p.step === "mythpath" && p.status !== "completed");



  return (
    <OnboardingWrapper>
    <div className="container my-4">
      <div className="d-flex justify-content-end mb-2">
        <button
          className="btn btn-sm btn-outline-secondary"
          onClick={() => toggle()}
        >
          {theme === "fantasy" ? "\uD83D\uDCBC Plain English" : "\uD83E\uDDD9 Wizard Terms"}
        </button>
      </div>
      <GuideChatPanel />
      <OnboardingIntroModal />
      <OnboardingProgressBar />
      <OnboardingProgressPanel />
      <div className="d-flex justify-content-between align-items-center">
        <h2>{ONBOARDING_WORLD.title}</h2>
        <div className="btn-group">
          <button
            className={`btn btn-sm ${
              theme === "fantasy" ? "btn-primary" : "btn-outline-primary"
            }`}
            onClick={() => toggle("fantasy")}
          >
            🧙 Fantasy
          </button>
          <button
            className={`btn btn-sm ${
              theme === "practical" ? "btn-primary" : "btn-outline-primary"
            }`}
            onClick={() => toggle("practical")}
          >
            💼 Practical
          </button>
        </div>
      </div>
      {mythIncomplete && (
        <div className="alert alert-info mt-3">Start Here → Mythpath</div>
      )}
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

                  {node.emoji} {theme === "fantasy" ? node.title : node.ui_label || node.title}

                </h5>
                <small className="text-muted">{status}</small>
              </div>
              <OverlayTrigger
                placement="top"

                overlay={<Tooltip>{node.tooltip || node.description}</Tooltip>}

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
        <button className="btn btn-success" onClick={() => navigate("/assistants/create")}>Launch Your Assistant!</button>
      </div>
      <OnboardingHelpButton />
    </div>
    </OnboardingWrapper>
  );
}
